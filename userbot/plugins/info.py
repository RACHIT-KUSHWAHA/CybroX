#  Legendbot - Advanced Telegram Automation
#  Copyright (C) 2025 Legendbot Organization

#chup

import os
import sys
import time
import platform
import datetime
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.types import Message, User

from userbot.helpers.misc import modules_help, prefix, python_version, userbot_version
from userbot.helpers.managers import edit_or_reply

# --- Helpers ---

async def get_user_info(client: Client, message: Message):
    """Get user object from message"""
    user = None
    if len(message.command) > 1:
        try:
            user = await client.get_users(message.command[1])
        except Exception:
            pass
    
    if not user and message.reply_to_message:
        user = message.reply_to_message.from_user
        
    if not user:
        user = message.from_user
        
    return user

def get_status_string(user: User):
    """Get user status string"""
    if not user.status:
        return "None"
    
    status = user.status
    if status == enums.UserStatus.ONLINE:
        return "Online 🟢"
    elif status == enums.UserStatus.OFFLINE:
        if user.last_online_date:
            return f"Offline (Last seen: {user.last_online_date.strftime('%Y-%m-%d %H:%M:%S')}) 🔴"
        return "Offline 🔴"
    elif status == enums.UserStatus.RECENTLY:
        return "Recently 🟡"
    elif status == enums.UserStatus.LAST_WEEK:
        return "Last Week 🟡"
    elif status == enums.UserStatus.LAST_MONTH:
        return "Last Month 🟡"
    elif status == enums.UserStatus.LONG_AGO:
        return "Long Ago ⚪"
    return str(status)

# --- Commands ---

@Client.on_message(filters.command(["whois", "info", "user"], prefix) & filters.me)
async def whois_cmd(client: Client, message: Message):
    """Get detailed info about a user."""
    msg = await edit_or_reply(message, "<b>🔍 Fetching user info...</b>")
    
    user = await get_user_info(client, message)
    if not user:
        return await msg.edit("<b>❌ User not found!</b>")
    
    # Fetch full user details (for bio, etc.)
    try:
        full_user = await client.get_chat(user.id)
        bio = full_user.bio if full_user.bio else "None"
    except Exception:
        bio = "None"
        
    # Common Chats
    common_chats = 0
    try:
        common = await client.get_common_chats(user.id)
        common_chats = len(common)
    except Exception:
        pass
        
    # Profile Photo
    photo_id = user.photo.big_file_id if user.photo else None
    photo_path = None
    if photo_id:
        try:
            photo_path = await client.download_media(photo_id)
        except Exception:
            pass

    # Info Text
    text = f"<b>👤 User Info:</b>\n\n"
    text += f"<b>🆔 ID:</b> <code>{user.id}</code>\n"
    text += f"<b>👤 First Name:</b> {user.first_name}\n"
    if user.last_name:
        text += f"<b>👤 Last Name:</b> {user.last_name}\n"
    if user.username:
        text += f"<b>📧 Username:</b> @{user.username}\n"
    text += f"<b>🔗 Permalink:</b> <a href='tg://user?id={user.id}'>Link</a>\n"
    text += f"<b>🏢 DC ID:</b> {user.dc_id if user.dc_id else 'Unknown'}\n"
    text += f"<b>🔋 Status:</b> {get_status_string(user)}\n"
    text += f"<b>📝 Bio:</b> {bio}\n"
    text += f"<b>🤝 Common Chats:</b> {common_chats}\n"
    text += f"<b>🤖 Is Bot:</b> {'Yes' if user.is_bot else 'No'}\n"
    text += f"<b>🚫 Is Scam:</b> {'Yes' if user.is_scam else 'No'}\n"
    text += f"<b>📛 Is Fake:</b> {'Yes' if user.is_fake else 'No'}\n"
    if user.is_premium:
        text += f"<b>🌟 Premium:</b> Yes\n"

    if photo_path:
        await message.reply_photo(photo_path, caption=text)
        await msg.delete()
        os.remove(photo_path)
    else:
        await msg.edit(text)

@Client.on_message(filters.command(["id"], prefix) & filters.me)
async def id_cmd(client: Client, message: Message):
    """Get ID of current chat or replied user."""
    text = f"<b>Chat ID:</b> <code>{message.chat.id}</code>\n"
    
    if message.reply_to_message:
        text += f"<b>Replied User ID:</b> <code>{message.reply_to_message.from_user.id}</code>\n"
        if message.reply_to_message.forward_from:
            text += f"<b>Forwarded User ID:</b> <code>{message.reply_to_message.forward_from.id}</code>\n"
        if message.reply_to_message.forward_from_chat:
            text += f"<b>Forwarded Chat ID:</b> <code>{message.reply_to_message.forward_from_chat.id}</code>\n"
            
    await edit_or_reply(message, text)

@Client.on_message(filters.command(["sysinfo", "about", "bot"], prefix) & filters.me)
async def sysinfo_cmd(client: Client, message: Message):
    """Show system and bot information."""
    msg = await edit_or_reply(message, "<b>🖥️ Fetching system info...</b>")
    
    # Uptime
    uptime = datetime.timedelta(seconds=int(time.time() - client.start_time)) if hasattr(client, 'start_time') else "Unknown"
    
    text = f"<b>🤖 Legendbot System Info</b>\n\n"
    text += f"<b>🐍 Python:</b> <code>{python_version}</code>\n"
    text += f"<b>🔥 Pyrogram:</b> <code>{pyrogram.__version__}</code>\n"
    text += f"<b>📦 Version:</b> <code>{userbot_version}</code>\n"
    text += f"<b>💻 OS:</b> <code>{platform.system()} {platform.release()}</code>\n"
    text += f"<b>🏗️ Arch:</b> <code>{platform.machine()}</code>\n"
    text += f"<b>⏳ Uptime:</b> <code>{uptime}</code>\n"
    
    await msg.edit(text)

modules_help["info"] = {
    "whois [user/reply]": "Get detailed info about a user.",
    "id": "Get ID of chat or replied message.",
    "sysinfo": "Show system and bot information.",
    "__category__": "info"
}