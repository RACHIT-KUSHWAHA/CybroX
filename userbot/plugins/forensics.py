# Module: forensics.py
# Description: Forensic Mirror (Edit Logger)
# Copyright (C) 2025 CybroX UserBot Organization

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

from userbot.core.logger import LOGS
from userbot.helpers.misc import modules_help, prefix
from userbot.helpers.scripts import edit_or_reply
from userbot.helpers.db import db

# Configuration: We can toggle logging on/off
# Default: Log edits in PMs only to avoid group spam

@Client.on_message(filters.command(["forensics", "logedits"], prefix) & filters.me)
async def forensics_cmd(client: Client, message: Message):
    """Toggle Forensic Logger"""
    current = await db.get("forensics", "enabled", True)
    new_state = not current
    await db.set("forensics", "enabled", new_state)
    
    state_text = "Activated" if new_state else "Deactivated"
    await edit_or_reply(message, f"<b>🕵️ Forensic Mirror {state_text}.</b>\nEdited PMs will be logged to Saved Messages.")


@Client.on_edited_message(filters.private & ~filters.me & ~filters.bot & ~filters.service)
async def edit_logger(client: Client, message: Message):
    """Log Edited Messages to Saved Messages"""
    is_enabled = await db.get("forensics", "enabled", True)
    
    if is_enabled:
        try:
            sender = message.from_user.first_name if message.from_user else "Unknown"
            userid = message.from_user.id if message.from_user else 0
            
            # Construct Log Message
            log_text = (
                f"<b>🕵️ Forensic Alert: Message Edited</b>\n"
                f"<b>From:</b> <a href='tg://user?id={userid}'>{sender}</a> (<code>{userid}</code>)\n"
                f"<b>Chat:</b> Private\n"
                f"<b>Time:</b> {message.edit_date}\n\n"
                f"<b>⬇️ New Content Below ⬇️</b>"
            )
            
            # Send Log Header
            await client.send_message("me", log_text)
            
            # Forward the NEW version of the message
            # We forward so we keep media/formatting intact
            await message.forward("me")
            
        except Exception as e:
            # Ssst, don't tell them we failed to spy
            LOGS.error(f"Forensics Error: {str(e)}")


modules_help["forensics"] = {
    "forensics": "Toggle edit logging (Default: ON)",
    "logedits": "Alias for forensics",
    "__category__": "security"
}
