# Module: zombies.py
# Description: Clean deleted accounts from groups
# Copyright (C) 2025 CybroX UserBot Organization

import asyncio
from pyrogram import Client, filters, errors
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

from userbot.helpers.misc import modules_help, prefix
from userbot.helpers.scripts import edit_or_reply

@Client.on_message(filters.command(["zombies", "cleancheck"], prefix) & filters.me)
async def zombies_cmd(client: Client, message: Message):
    """Check for and ban deleted accounts"""
    # Check if silent mode requested
    silent = False
    if len(message.command) > 1 and message.command[1] in ["-s", "--silent"]:
        silent = True
        await message.delete()
    
    chat_id = message.chat.id
    
    # Send status message if not silent
    msg = None
    if not silent:
        msg = await edit_or_reply(message, "<b>🧟 Searching for zombies...</b>")
    
    # 1. Find Zombies
    zombie_ids = []
    try:
        # Iterate through all members
        async for member in client.get_chat_members(chat_id):
            if member.user.is_deleted:
                zombie_ids.append(member.user.id)
    except Exception as e:
        if msg:
            await msg.edit(f"<b>❌ Error scanning members:</b> {e}")
        return

    # If no zombies found
    if not zombie_ids:
        if msg:
            await msg.edit("<b>✅ No zombies found! This chat is clean.</b>")
            await asyncio.sleep(3)
            await msg.delete()
        return

    # 2. Confirm action if many zombies (optional safety, skipping for automation speed)
    # We will just proceed to clean them.
    
    if msg:
        await msg.edit(f"<b>🧟 Found {len(zombie_ids)} zombies! Exorcising...</b>")
    
    # 3. Ban Zombies (Kick = Ban + Unban)
    cleaned = 0
    failed = 0
    
    # Process in chunks of 50 to respect limits
    # Note: Telegram doesn't support mass kick, must iterate.
    for user_id in zombie_ids:
        try:
            # Ban
            await client.ban_chat_member(chat_id, user_id)
            # Unban immediately to remove from ban list (just kick)
            await asyncio.sleep(0.1) # Small delay
            await client.unban_chat_member(chat_id, user_id)
            cleaned += 1
            
            # Update progress every 10 users if not silent
            if not silent and cleaned % 10 == 0:
                await msg.edit(f"<b>🧟 Exorcising... ({cleaned}/{len(zombie_ids)})</b>")
            
        except errors.FloodWait as e:
            await asyncio.sleep(e.value)
            # Retry once
            try:
                await client.ban_chat_member(chat_id, user_id)
                await client.unban_chat_member(chat_id, user_id)
                cleaned += 1
            except:
                failed += 1
        except Exception:
            failed += 1
            
        await asyncio.sleep(0.5) # Prevent global flood
        
    # 4. Final Report
    if not silent:
        report = f"<b>🧟 Zombie Exorcism Complete!</b>\n\n"
        report += f"<b>Found:</b> {len(zombie_ids)}\n"
        report += f"<b>Cleaned:</b> {cleaned}\n"
        if failed > 0:
            report += f"<b>Failed:</b> {failed}"
            
        await msg.edit(report)
        # Delete report after 10 seconds
        await asyncio.sleep(10)
        await msg.delete()
    else:
        # In silent mode, maybe just log to Saved Messages?
        # For now, do nothing as requested "silent"
        pass

modules_help["zombies"] = {
    "zombies": "Check and remove deleted accounts from group",
    "zombies -s": "Silent mode (no messages)",
    "cleancheck": "Alias for zombies",
    "__category__": "admin"
}
