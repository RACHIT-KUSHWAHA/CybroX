#  Legendbot - Advanced Telegram Automation
#  Copyright (C) 2025 Legendbot Organization

import asyncio
import io
import time
from datetime import datetime, timedelta
from typing import Optional, Union, Tuple

from pyrogram import Client, filters, errors, enums
from pyrogram.types import Message, ChatPermissions, ChatAdministratorRights
from pyrogram.errors import UserAdminInvalid, ChatAdminRequired

from userbot.helpers.misc import modules_help, prefix
from userbot.helpers.managers import edit_or_reply
from userbot.helpers.config import Config as config

# --- Helpers ---

async def send_large_output(message: Message, text: str, filename: str = "output.txt"):
    """Send text as file if too long"""
    if len(text) > 4000:
        f = io.BytesIO(text.encode("utf-8"))
        f.name = filename
        await message.reply_document(f, caption=f"Output for {filename}")
        if message.from_user.is_self:
            await message.delete()
    else:
        await edit_or_reply(message, text)

async def get_user_reason(client: Client, message: Message) -> Tuple[Optional[int], Optional[str], Optional[str]]:
    """
    Extract user, reason and time from command.
    Returns: (user_id, reason, time_seconds)
    """
    user_id = None
    reason = None
    time_seconds = 0
    
    args = message.command[1:]
    
    # 1. Check Reply
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    
    # 2. Check Arguments
    if args:
        # If no reply, first arg might be user
        if not user_id:
            try:
                user = await client.get_users(args[0])
                user_id = user.id
                args.pop(0) # Remove user from args
            except Exception:
                pass
        
        # Check for time in remaining args
        if args:
            # Check first remaining arg for time
            t_str = args[0]
            if t_str[-1].lower() in ['m', 'h', 'd', 'w'] and t_str[:-1].isdigit():
                unit = t_str[-1].lower()
                val = int(t_str[:-1])
                if unit == 'm': time_seconds = val * 60
                elif unit == 'h': time_seconds = val * 3600
                elif unit == 'd': time_seconds = val * 86400
                elif unit == 'w': time_seconds = val * 604800
                args.pop(0) # Remove time from args
            
            # Rest is reason
            if args:
                reason = " ".join(args)

    return user_id, reason, time_seconds

async def check_admin(client: Client, message: Message, permission: str) -> bool:
    """Check if user and bot have permissions"""
    # 1. Check Bot Perms
    try:
        bot = await message.chat.get_member(client.me.id)
        if not getattr(bot.privileges, permission, False):
            await edit_or_reply(message, f"❌ <b>I need <code>{permission}</code> permission!</b>")
            return False
    except Exception:
        await edit_or_reply(message, "❌ <b>I am not an admin here!</b>")
        return False

    # 2. Check User Perms (if not Owner)
    if message.from_user.id not in [config.OWNER_ID] and message.chat.owner_id != message.from_user.id:
        try:
            user = await message.chat.get_member(message.from_user.id)
            if not getattr(user.privileges, permission, False):
                await edit_or_reply(message, f"❌ <b>You need <code>{permission}</code> permission!</b>")
                return False
        except Exception:
            pass # Should not happen for admin commands usually
            
    return True

# --- Commands ---

@Client.on_message(filters.command(["ban", "b"], prefix) & filters.me)
async def ban_cmd(client: Client, message: Message):
    """Ban a user. Usage: .ban [user] [time] [reason]"""
    user_id, reason, duration = await get_user_reason(client, message)
    
    if not user_id:
        return await edit_or_reply(message, "<b>❌ User not found. Reply or specify username/ID.</b>")
    
    if user_id == client.me.id:
        return await edit_or_reply(message, "<b>❌ I can't ban myself.</b>")

    try:
        until = datetime.now() + timedelta(seconds=duration) if duration > 0 else datetime.now() + timedelta(days=3650) # Forever
        
        await client.ban_chat_member(message.chat.id, user_id, until_date=until)
        
        user = await client.get_users(user_id)
        mention = user.mention if user else f"<code>{user_id}</code>"
        
        text = f"<b>🚫 Banned:</b> {mention}"
        if duration > 0:
            text += f"\n<b>⏳ Time:</b> {timedelta(seconds=duration)}"
        if reason:
            text += f"\n<b>📝 Reason:</b> {reason}"
            
        await edit_or_reply(message, text)
        
    except Exception as e:
        await edit_or_reply(message, f"<b>❌ Error:</b> {e}")

@Client.on_message(filters.command(["unban", "ub"], prefix) & filters.me)
async def unban_cmd(client: Client, message: Message):
    """Unban a user."""
    user_id, _, _ = await get_user_reason(client, message)
    if not user_id:
        return await edit_or_reply(message, "<b>❌ User not found.</b>")

    try:
        await client.unban_chat_member(message.chat.id, user_id)
        user = await client.get_users(user_id)
        await edit_or_reply(message, f"<b>✅ Unbanned:</b> {user.mention if user else user_id}")
    except Exception as e:
        await edit_or_reply(message, f"<b>❌ Error:</b> {e}")

@Client.on_message(filters.command(["mute", "m"], prefix) & filters.me)
async def mute_cmd(client: Client, message: Message):
    """Mute a user. Usage: .mute [user] [time] [reason]"""
    user_id, reason, duration = await get_user_reason(client, message)
    
    if not user_id:
        return await edit_or_reply(message, "<b>❌ User not found.</b>")

    try:
        until = datetime.now() + timedelta(seconds=duration) if duration > 0 else datetime.now() + timedelta(days=3650)
        permissions = ChatPermissions(can_send_messages=False)
        
        await client.restrict_chat_member(message.chat.id, user_id, permissions, until_date=until)
        
        user = await client.get_users(user_id)
        mention = user.mention if user else f"<code>{user_id}</code>"
        
        text = f"<b>🔇 Muted:</b> {mention}"
        if duration > 0:
            text += f"\n<b>⏳ Time:</b> {timedelta(seconds=duration)}"
        if reason:
            text += f"\n<b>📝 Reason:</b> {reason}"
            
        await edit_or_reply(message, text)
    except Exception as e:
        await edit_or_reply(message, f"<b>❌ Error:</b> {e}")

@Client.on_message(filters.command(["unmute", "um"], prefix) & filters.me)
async def unmute_cmd(client: Client, message: Message):
    """Unmute a user."""
    user_id, _, _ = await get_user_reason(client, message)
    if not user_id:
        return await edit_or_reply(message, "<b>❌ User not found.</b>")

    try:
        # Restore default permissions (usually allows sending messages)
        # We need to check chat default permissions or just set can_send_messages=True
        chat = await client.get_chat(message.chat.id)
        # Fallback to standard permissions if chat permissions fetch fails or is complex
        perms = chat.permissions if chat.permissions else ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_send_polls=True
        )
        
        await client.restrict_chat_member(message.chat.id, user_id, perms)
        user = await client.get_users(user_id)
        await edit_or_reply(message, f"<b>🔊 Unmuted:</b> {user.mention if user else user_id}")
    except Exception as e:
        await edit_or_reply(message, f"<b>❌ Error:</b> {e}")

@Client.on_message(filters.command(["kick", "k"], prefix) & filters.me)
async def kick_cmd(client: Client, message: Message):
    """Kick a user."""
    user_id, reason, _ = await get_user_reason(client, message)
    if not user_id:
        return await edit_or_reply(message, "<b>❌ User not found.</b>")

    try:
        await client.ban_chat_member(message.chat.id, user_id)
        await client.unban_chat_member(message.chat.id, user_id) # Unban immediately to allow rejoin
        
        user = await client.get_users(user_id)
        text = f"<b>👢 Kicked:</b> {user.mention if user else user_id}"
        if reason:
            text += f"\n<b>📝 Reason:</b> {reason}"
        await edit_or_reply(message, text)
    except Exception as e:
        await edit_or_reply(message, f"<b>❌ Error:</b> {e}")

@Client.on_message(filters.command(["pin"], prefix) & filters.me)
async def pin_cmd(client: Client, message: Message):
    """Pin a message. Usage: .pin [loud/notify]"""
    if not message.reply_to_message:
        return await edit_or_reply(message, "<b>❌ Reply to a message to pin it.</b>")
    
    disable_notification = True
    if len(message.command) > 1 and message.command[1].lower() in ["loud", "notify", "alert"]:
        disable_notification = False
        
    try:
        await message.reply_to_message.pin(disable_notification=disable_notification)
        await edit_or_reply(message, f"<b>📌 Pinned!</b> (Notify: {'Yes' if not disable_notification else 'No'})")
    except Exception as e:
        await edit_or_reply(message, f"<b>❌ Error:</b> {e}")

@Client.on_message(filters.command(["unpin"], prefix) & filters.me)
async def unpin_cmd(client: Client, message: Message):
    """Unpin a message."""
    if not message.reply_to_message:
        return await edit_or_reply(message, "<b>❌ Reply to a message to unpin it.</b>")
        
    try:
        await message.reply_to_message.unpin()
        await edit_or_reply(message, "<b>📍 Unpinned!</b>")
    except Exception as e:
        await edit_or_reply(message, f"<b>❌ Error:</b> {e}")

@Client.on_message(filters.command(["promote", "fullpromote"], prefix) & filters.me)
async def promote_cmd(client: Client, message: Message):
    """Promote a user. Usage: .promote [user] [title]"""
    user_id, title, _ = await get_user_reason(client, message)
    if not user_id:
        return await edit_or_reply(message, "<b>❌ User not found.</b>")
    
    if not title:
        title = "Admin"

    try:
        # Full Promote
        await client.promote_chat_member(
            message.chat.id,
            user_id,
            privileges=ChatAdministratorRights(
                can_change_info=True,
                can_invite_users=True,
                can_delete_messages=True,
                can_restrict_members=True,
                can_pin_messages=True,
                can_promote_members=True,
                can_manage_chat=True,
                can_manage_video_chats=True
            )
        )
        # Set Title
        try:
            await client.set_administrator_title(message.chat.id, user_id, title)
        except:
            pass # Some chats don't support titles or bot lacks permission
            
        user = await client.get_users(user_id)
        await edit_or_reply(message, f"<b>👮 Promoted:</b> {user.mention if user else user_id}\n<b>Title:</b> {title}")
    except Exception as e:
        await edit_or_reply(message, f"<b>❌ Error:</b> {e}")

@Client.on_message(filters.command(["demote"], prefix) & filters.me)
async def demote_cmd(client: Client, message: Message):
    """Demote a user."""
    user_id, _, _ = await get_user_reason(client, message)
    if not user_id:
        return await edit_or_reply(message, "<b>❌ User not found.</b>")

    try:
        await client.promote_chat_member(
            message.chat.id,
            user_id,
            privileges=ChatAdministratorRights(
                can_change_info=False,
                can_invite_users=False,
                can_delete_messages=False,
                can_restrict_members=False,
                can_pin_messages=False,
                can_promote_members=False,
                can_manage_chat=False,
                can_manage_video_chats=False
            )
        )
        user = await client.get_users(user_id)
        await edit_or_reply(message, f"<b>📉 Demoted:</b> {user.mention if user else user_id}")
    except Exception as e:
        await edit_or_reply(message, f"<b>❌ Error:</b> {e}")

@Client.on_message(filters.command(["admins"], prefix) & filters.me)
async def admins_cmd(client: Client, message: Message):
    """List admins in chat."""
    msg = await edit_or_reply(message, "<b>👮 Fetching admins...</b>")
    admins = []
    try:
        async for member in client.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            admins.append(member)
            
        text = f"<b>👮 Admins in {message.chat.title}:</b>\n\n"
        for admin in admins:
            user = admin.user
            status = "👑" if admin.status == enums.ChatMemberStatus.OWNER else "👮"
            if user.is_deleted:
                name = "Deleted Account"
            else:
                name = user.first_name
            text += f"{status} <a href='tg://user?id={user.id}'>{name}</a>\n"
            
        await send_large_output(msg, text, "admins.txt")
    except Exception as e:
        await msg.edit(f"<b>❌ Error:</b> {e}")

@Client.on_message(filters.command(["bots"], prefix) & filters.me)
async def bots_cmd(client: Client, message: Message):
    """List bots in chat."""
    msg = await edit_or_reply(message, "<b>🤖 Fetching bots...</b>")
    bots = []
    try:
        async for member in client.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.BOTS):
            bots.append(member.user)
            
        text = f"<b>🤖 Bots in {message.chat.title}:</b>\n\n"
        for bot in bots:
            text += f"🤖 <a href='tg://user?id={bot.id}'>{bot.first_name}</a>\n"
            
        await send_large_output(msg, text, "bots.txt")
    except Exception as e:
        await msg.edit(f"<b>❌ Error:</b> {e}")

modules_help["admin"] = {
    "ban [user] [time] [reason]": "Ban a user. Time: 1m, 1h, 1d.",
    "unban [user]": "Unban a user.",
    "mute [user] [time] [reason]": "Mute a user.",
    "unmute [user]": "Unmute a user.",
    "kick [user]": "Kick a user.",
    "pin [loud]": "Pin a message.",
    "unpin": "Unpin a message.",
    "promote [user] [title]": "Promote a user.",
    "demote [user]": "Demote a user.",
    "admins": "List chat admins.",
    "bots": "List chat bots.",
    "__category__": "admin"
}