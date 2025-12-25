#  CybroX-UserBot - telegram userbot
#  Copyright (C) 2025 CybroX UserBot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import MessageDeleteForbidden, FloodWait

from userbot.helpers.misc import modules_help, prefix
from userbot.helpers.scripts import edit_or_reply, with_reply


@Client.on_message(filters.command("purge", prefix) & filters.me)
async def purge_cmd(client: Client, message: Message):
    """Delete messages. Reply to start point, OR use time argument (.purge 2h)."""
    
    # Mode 1: Time-based Purge
    if len(message.command) > 1:
        arg = message.command[1]
        seconds = 0
        try:
            if arg.endswith("s"): seconds = int(arg[:-1])
            elif arg.endswith("m"): seconds = int(arg[:-1]) * 60
            elif arg.endswith("h"): seconds = int(arg[:-1]) * 3600
            elif arg.endswith("d"): seconds = int(arg[:-1]) * 86400
            else: seconds = int(arg)  # Default to seconds? Or fail.
        except ValueError:
            await edit_or_reply(message, "<b>❌ Invalid format! Use 30s, 5m, 2h.</b>")
            return
            
        if seconds <= 0:
             return

        msg = await edit_or_reply(message, f"<b>🧹 Purging last {arg}...</b>")
        cutoff_time = time.time() - seconds
        
        chat_id = message.chat.id
        message_ids = []
        count = 0
        
        async for hist_msg in client.get_chat_history(chat_id):
            # Stop if we reach messages older than cutoff
            if hist_msg.date.timestamp() < cutoff_time:
                break
            
            # Don't delete the command message or confirmation yet
            if hist_msg.id == msg.id:
                continue
                
            message_ids.append(hist_msg.id)
            count += 1
            
            if len(message_ids) >= 100:
                try:
                    await client.delete_messages(chat_id, message_ids)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    await client.delete_messages(chat_id, message_ids)
                except MessageDeleteForbidden:
                    pass
                message_ids = []
                await asyncio.sleep(0.5)

        if message_ids:
             try:
                await client.delete_messages(chat_id, message_ids)
             except: pass
        
        await msg.edit(f"<b>🧹 Purged messages from last {arg}!</b>")
        await asyncio.sleep(3)
        await msg.delete()
        return

    # Mode 2: Reply-based Purge (Legacy)
    replied = await with_reply(message)
    if not replied:
        await edit_or_reply(message, "<b>❌ Reply to a message or use time (e.g., .purge 10m)</b>")
        return
        
    msg = await edit_or_reply(message, "<b>🧹 Purging messages...</b>")
    
    message_ids = []
    chat_id = message.chat.id
    
    # Get all message IDs to delete
    # [Rest of legacy logic]
    # Note: Using get_chat_history usually better than range if IDs are not sequential, 
    # but range is faster if they are. Pyrogram IDs are sequential per chat usually.
    # We will keep the original range logic for consistency if keys are sequential.
    # However, to be safe, we'll execute the original logic below.
    
    for message_id in range(replied.id, message.id + 1):
        message_ids.append(message_id)
        
        # Delete in chunks of 100 to avoid hitting limits
        if len(message_ids) == 100:
            try:
                await client.delete_messages(chat_id, message_ids)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await client.delete_messages(chat_id, message_ids)
            except MessageDeleteForbidden:
                await msg.edit("<b>❌ Cannot delete all messages. Try as admin.</b>")
                return
            message_ids = []
            await asyncio.sleep(0.5)  # Prevent flood
    
    # Delete any remaining messages
    if message_ids:
        try:
            await client.delete_messages(chat_id, message_ids)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await client.delete_messages(chat_id, message_ids)
        except MessageDeleteForbidden:
            pass
    
    # Send success message
    count = message.id - replied.id + 1
    await client.send_message(
        chat_id,
        f"<b>🧹 Purged {count} messages!</b>", 
        disable_notification=True
    )
    
    # Delete success message after 5 seconds
    # msg acts as our status message, we can just delete it or the new one
    try:
        await msg.delete()
    except: pass  # In case it was deleted
    
    succ_msg = await client.send_message(
        chat_id,
        f"<b>✅ Success message will be deleted in 5 seconds.</b>",
        disable_notification=True
    )
    await asyncio.sleep(5)
    await succ_msg.delete()


@Client.on_message(filters.command("del", prefix) & filters.me)
async def del_cmd(client: Client, message: Message):
    """Delete replied message"""
    replied = message.reply_to_message
    
    if not replied:
        await message.delete()
        return
        
    try:
        await replied.delete()
        await message.delete()
    except MessageDeleteForbidden:
        await edit_or_reply(message, "<b>❌ I don't have permission to delete this message.</b>")
        await asyncio.sleep(2)
        await message.delete()


@Client.on_message(filters.command("sd", prefix) & filters.me)
async def selfdestruct_cmd(client: Client, message: Message):
    """Send self-destructing message"""
    if len(message.command) < 3:
        await edit_or_reply(message, "<b>❌ Usage: </b><code>.sd [seconds] [text]</code>")
        await asyncio.sleep(3)
        await message.delete()
        return
    
    # Get seconds and text
    try:
        seconds = int(message.command[1])
        if seconds < 1 or seconds > 86400:  # max 24 hours
            raise ValueError("Invalid time")
    except ValueError:
        await edit_or_reply(message, "<b>❌ Time must be between 1 second and 24 hours.</b>")
        await asyncio.sleep(3)
        await message.delete()
        return
    
    text = message.text.split(None, 2)[2]
    
    # Delete the command message
    await message.delete()
    
    # Send the self-destructing message
    msg = await client.send_message(
        message.chat.id,
        f"{text}\n\n<b>⏳ Self-destructing in {seconds} seconds</b>"
    )
    
    # Sleep and delete
    await asyncio.sleep(seconds)
    try:
        await msg.delete()
    except:
        pass


@Client.on_message(filters.command("clear", prefix) & filters.me)
async def clear_cmd(client: Client, message: Message):
    """Clear the chat by sending 100 blank lines"""
    await message.delete()
    
    # Send message with 100 newlines
    clear_text = "\n" * 100 + "<b>Chat cleared! 🧹</b>"
    
    await client.send_message(
        message.chat.id,
        clear_text
    )


@Client.on_message(filters.command(["purgeme", "pm"], prefix) & filters.me)
async def purgeme_cmd(client: Client, message: Message):
    """Delete X messages from yourself"""
    if len(message.command) <= 1:
        await edit_or_reply(message, "<b>❌ Usage: </b><code>.purgeme [count]</code>")
        await asyncio.sleep(3)
        await message.delete()
        return
    
    try:
        count = int(message.command[1])
        if count < 1 or count > 1000:
            raise ValueError("Invalid count")
    except ValueError:
        await edit_or_reply(message, "<b>❌ Count must be between 1 and 1000.</b>")
        await asyncio.sleep(3)
        await message.delete()
        return
    
    await message.delete()
    
    # Get your own messages
    message_ids = []
    total_count = 0
    
    async for msg in client.get_chat_history(message.chat.id, limit=1000):
        if msg.from_user and msg.from_user.is_self:
            message_ids.append(msg.id)
            total_count += 1
            
            if total_count >= count:
                break
            
            # Delete in chunks of 100 to avoid hitting limits
            if len(message_ids) == 100:
                try:
                    await client.delete_messages(message.chat.id, message_ids)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    await client.delete_messages(message.chat.id, message_ids)
                except MessageDeleteForbidden:
                    pass
                message_ids = []
                await asyncio.sleep(0.5)  # Prevent flood
    
    # Delete any remaining messages
    if message_ids:
        try:
            await client.delete_messages(message.chat.id, message_ids)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await client.delete_messages(message.chat.id, message_ids)
        except MessageDeleteForbidden:
            pass
    
    # Send success message and delete it after 3 seconds
    msg = await client.send_message(
        message.chat.id,
        f"<b>🧹 Purged {total_count} of your messages!</b>",
        disable_notification=True
    )
    await asyncio.sleep(3)
    await msg.delete()


modules_help["purge"] = {
    "purge": "Delete all messages from replied to current",
    "del": "Delete replied message",
    "sd [seconds] [text]": "Send self-destructing message",
    "clear": "Clear the chat with blank lines",
    "purgeme [count]": "Delete your last X messages",
    "pm [count]": "Alias for purgeme command",
    "__category__": "utils"
}