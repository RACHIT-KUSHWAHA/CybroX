# Module: ghost.py
# Description: Ghost Protocol (Shadow Inbox & Anti-Read Receipt)
# Copyright (C) 2025 CybroX UserBot Organization

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

from userbot.helpers.misc import modules_help, prefix
from userbot.helpers.scripts import edit_or_reply
from userbot.helpers.db import db

@Client.on_message(filters.command(["ghost", "stealth"], prefix) & filters.me)
async def ghost_cmd(client: Client, message: Message):
    """Toggle Ghost Mode (Shadow Inbox)"""
    if len(message.command) > 1:
        action = message.command[1].lower()
        if action in ["on", "true", "enable"]:
            await db.set("ghost", "enabled", True)
            await edit_or_reply(message, "<b>👻 Ghost Protocol Activated.</b>\nIncoming PMs will be forwarded to Saved Messages.")
        elif action in ["off", "false", "disable"]:
            await db.set("ghost", "enabled", False)
            await edit_or_reply(message, "<b>👻 Ghost Protocol Deactivated.</b>\nYou are now visible.")
        else:
            await edit_or_reply(message, "<b>❌ Usage:</b> .ghost [on/off]")
    else:
        # Toggle current state
        current = await db.get("ghost", "enabled", False)
        new_state = not current
        await db.set("ghost", "enabled", new_state)
        state_text = "Activated" if new_state else "Deactivated"
        info_text = "Incoming PMs will be forwarded to Saved Messages." if new_state else "You are now visible."
        await edit_or_reply(message, f"<b>👻 Ghost Protocol {state_text}.</b>\n{info_text}")

@Client.on_message(filters.command("peek", prefix) & filters.me)
async def peek_cmd(client: Client, message: Message):
    """Peek into a chat without entering (No Read Receipt)"""
    if len(message.command) < 2:
        await edit_or_reply(message, "<b>❌ Usage:</b> .peek @username [limit]")
        return
        
    target = message.command[1]
    limit = 5
    if len(message.command) > 2 and message.command[2].isdigit():
        limit = int(message.command[2])
        
    msg = await edit_or_reply(message, f"<b>👀 Peeking last {limit} messages from {target}...</b>")
    
    try:
        # Get chat info first
        chat = await client.get_chat(target)
        
        # Get history
        messages = []
        async for m in client.get_chat_history(chat.id, limit=limit):
            messages.append(m)
            
        # Reverse to show oldest first in the report
        messages.reverse()
        
        if not messages:
            await msg.edit("<b>❌ No messages found.</b>")
            return
            
        # We process them into a readable format in Saved Messages or edit the current message
        # Since we want to avoid reading, we should NOT print them in the chat we are peeking if we were inside it (but we assume we are not).
        # We will forward them to Saved Messages or print a summary here.
        # Printing summary here is better for UX.
        
        output = f"<b>👀 Peek Report: {chat.title or chat.first_name}</b>\n\n"
        
        for m in messages:
            sender = m.from_user.first_name if m.from_user else "Unknown"
            # Truncate text
            text = m.text or m.caption or "[Media]"
            if len(text) > 50:
                text = text[:50] + "..."
                
            output += f"<b>{sender}:</b> {text}\n"
            
        await msg.edit(output)
        
    except Exception as e:
        await msg.edit(f"<b>❌ Error peeking:</b> {e}")

# Ghost Interceptor
# Priority: High (Group 1) to catch them before other handlers if needed, 
# but Pyrogram handles all groups asynchronously. 
@Client.on_message(filters.private & ~filters.me & ~filters.bot & ~filters.service, group=1)
async def ghost_interceptor(client: Client, message: Message):
    """Intercept and Forward if Ghost Mode is On"""
    is_ghost = await db.get("ghost", "enabled", False)
    
    if is_ghost:
        try:
            # We assume 'me' (Saved Messages) is always safe
            # Determine sender name for clarity
            sender = message.from_user.first_name if message.from_user else "Unknown"
            
            # Forward with a header to Saved Messages
            # We use send_message instead of forward_messages to add context/header if we want,
            # but forward preserves media best.
            # Let's verify if we can send a "Ghost Notification" then the message.
            
            # Note: We cannot prevent the server from marking it as 'received' (one tick),
            # but strictly speaking, we are NOT calling read_history. 
            # If the user opens the "Saved Messages" chat, they read THIS message, not the original.
            
            await client.send_message(
                "me", 
                f"<b>👻 Shadow Inbox - Incoming from {sender} ({message.from_user.id})</b>"
            )
            await message.forward("me")
            
            # Important: We do NOT stop propagation. Other modules (like pmpermit) might still need to run if they reply?
            # If ghost mode is strictly "Stealth", we might want to prevent PM Permit from Replying?
            # Actually, if PM Permit replies, it reveals we are online/bot is active.
            # So Ghost Mode should probably STOP propagation to prevent PMPermit from auto-replying.
            
            message.stop_propagation()
            
        except Exception as e:
            print(f"Ghost Error: {e}")

modules_help["ghost"] = {
    "ghost [on/off]": "Toggle Ghost Protocol (Shadow Inbox)",
    "peek [user]": "Read messages without triggering read receipt",
    "stealth": "Alias for ghost",
    "__category__": "privacy"
}
