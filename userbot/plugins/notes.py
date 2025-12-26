#  Legendbot-UserBot - telegram userbot
#  Copyright (C) 2025 Legendbot UserBot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

from userbot.helpers.misc import modules_help, prefix
from userbot.helpers.managers import edit_or_reply, with_reply
from userbot.helpers.db import db


@Client.on_message(filters.command("save", prefix) & filters.me)
async def save_note(client: Client, message: Message):
    """Save a note"""
    if len(message.command) < 2:
        await edit_or_reply(message, "<b>Not enough arguments!</b>\nUsage: .save [name] [content or reply]")
        await asyncio.sleep(3)
        await message.delete()
        return
    
    note_name = message.command[1].lower()
    
    # If replying to a message
    if message.reply_to_message:
        # Try to save text content
        if message.reply_to_message.text:
            note_content = message.reply_to_message.text.markdown
            note_type = "text"
        elif message.reply_to_message.caption:
            note_content = message.reply_to_message.caption.markdown
            note_type = "caption"
        # Try to save media
        elif message.reply_to_message.photo:
            note_content = message.reply_to_message.photo.file_id
            note_type = "photo"
        elif message.reply_to_message.document:
            note_content = message.reply_to_message.document.file_id
            note_type = "document"
        elif message.reply_to_message.video:
            note_content = message.reply_to_message.video.file_id
            note_type = "video"
        elif message.reply_to_message.audio:
            note_content = message.reply_to_message.audio.file_id
            note_type = "audio"
        elif message.reply_to_message.voice:
            note_content = message.reply_to_message.voice.file_id
            note_type = "voice"
        elif message.reply_to_message.sticker:
            note_content = message.reply_to_message.sticker.file_id
            note_type = "sticker"
        else:
            await edit_or_reply(message, "<b>Unsupported message type!</b>")
            await asyncio.sleep(3)
            await message.delete()
            return
            
        # Save additional caption if provided
        if len(message.command) > 2 and (note_type != "text" and note_type != "caption"):
            note_caption = " ".join(message.command[2:])
        else:
            note_caption = message.reply_to_message.caption or ""
    else:
        # If direct text provided
        if len(message.command) < 3:
            await edit_or_reply(message, "<b>Not enough arguments!</b>\nUsage: .save [name] [content]")
            await asyncio.sleep(3)
            await message.delete()
            return
            
        note_content = " ".join(message.command[2:])
        note_type = "text"
        note_caption = ""
    
    # Save note to database
    # Fix: Await get, then modify, then await set
    notes = await db.get("notes", "notes", {})
    notes[note_name] = {
        "type": note_type,
        "content": note_content,
        "caption": note_caption
    }
    await db.set("notes", "notes", notes)
    
    await edit_or_reply(message, f"<b>Note '{note_name}' saved successfully!</b>")
    await asyncio.sleep(2)
    await message.delete()


@Client.on_message(filters.command("get", prefix) & filters.me)
async def get_note(client: Client, message: Message):
    """Retrieve a saved note"""
    if len(message.command) < 2:
        await edit_or_reply(message, "<b>Not enough arguments!</b>\nUsage: .get [name]")
        await asyncio.sleep(3)
        await message.delete()
        return
    
    note_name = message.command[1].lower()
    notes = await db.get("notes", "notes", {})
    
    if note_name not in notes:
        await edit_or_reply(message, f"<b>Note '{note_name}' not found!</b>")
        await asyncio.sleep(3)
        await message.delete()
        return
    
    note = notes[note_name]
    await message.delete()
    
    # Simple senders could benefit from a helper, but explicit is fine
    if note["type"] == "text":
        await client.send_message(
            message.chat.id,
            note["content"],
            disable_web_page_preview=True
        )
    elif note["type"] == "caption":
        await client.send_message(
            message.chat.id,
            note["content"],
            disable_web_page_preview=True
        )
    elif note["type"] == "photo":
        await client.send_photo(
            message.chat.id,
            note["content"],
            caption=note["caption"]
        )
    elif note["type"] == "document":
        await client.send_document(
            message.chat.id,
            note["content"],
            caption=note["caption"]
        )
    elif note["type"] == "video":
        await client.send_video(
            message.chat.id,
            note["content"],
            caption=note["caption"]
        )
    elif note["type"] == "audio":
        await client.send_audio(
            message.chat.id,
            note["content"],
            caption=note["caption"]
        )
    elif note["type"] == "voice":
        await client.send_voice(
            message.chat.id,
            note["content"],
            caption=note["caption"]
        )
    elif note["type"] == "sticker":
        await client.send_sticker(
            message.chat.id,
            note["content"]
        )


@Client.on_message(filters.command("notes", prefix) & filters.me)
async def list_notes(client: Client, message: Message):
    """List all saved notes"""
    notes = await db.get("notes", "notes", {})
    
    if not notes:
        await edit_or_reply(message, "<b>No notes found!</b>")
        await asyncio.sleep(3)
        await message.delete()
        return
    
    text = "<b>Saved notes:</b>\n"
    for name in sorted(notes.keys()):
        text += f"• <code>{name}</code>: {notes[name]['type']}\n"
    
    await edit_or_reply(message, text)


@Client.on_message(filters.command("clear", prefix) & filters.me)
async def clear_note(client: Client, message: Message):
    """Delete a saved note"""
    if len(message.command) < 2:
        await edit_or_reply(message, "<b>Not enough arguments!</b>\nUsage: .clear [name]")
        await asyncio.sleep(3)
        await message.delete()
        return
    
    note_name = message.command[1].lower()
    notes = await db.get("notes", "notes", {})
    
    if note_name not in notes:
        await edit_or_reply(message, f"<b>Note '{note_name}' not found!</b>")
        await asyncio.sleep(3)
        await message.delete()
        return
    
    del notes[note_name]
    await db.set("notes", "notes", notes)
    
    await edit_or_reply(message, f"<b>Note '{note_name}' deleted successfully!</b>")
    await asyncio.sleep(2)
    await message.delete()


modules_help["notes"] = {
    "save [name] [text]": "Save a note with the given name and content (or reply to a message)",
    "get [name]": "Retrieve a saved note",
    "notes": "List all saved notes",
    "clear [name]": "Delete a saved note",
    "__category__": "utils"
}