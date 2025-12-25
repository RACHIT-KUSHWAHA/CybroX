from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus, ChatType
from userbot.helpers.misc import modules_help, prefix
from userbot.helpers.scripts import edit_or_reply
from userbot.helpers.db import liter

@Client.on_message(filters.command("fban", prefix) & filters.me)
async def fban_cmd(client: Client, message: Message):
    """
    Federation Ban: Ban a user from all your groups and add to DB.
    Usage: .fban <reply/user> [reason]
    """
    cmd = message.command
    user_id = None
    reason = "Malicious Activity"

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        if len(cmd) > 1:
            reason = " ".join(cmd[1:])
    elif len(cmd) > 1:
        # Resolve username/id
        try:
            user = await client.get_users(cmd[1])
            user_id = user.id
            if len(cmd) > 2:
                reason = " ".join(cmd[2:])
        except:
            await edit_or_reply(message, "<b>❌ Invalid User ID/Username.</b>")
            return

    if not user_id:
        await edit_or_reply(message, "<b>❌ Reply to a user or specify specific user.</b>")
        return

    # 1. Add to Database
    await liter.add_fban(user_id, reason, message.from_user.id)

    # 2. Ban in current chat
    try:
        await client.ban_chat_member(message.chat.id, user_id)
        text = f"<b>🚫 FedBanned!</b>\n<b>User:</b> <code>{user_id}</code>\n<b>Reason:</b> {reason}"
    except Exception as e:
        text = f"<b>🚫 FedBanned in DB, but failed here:</b> {e}"

    await edit_or_reply(message, text)


@Client.on_message(filters.command("unfban", prefix) & filters.me)
async def unfban_cmd(client: Client, message: Message):
    """
    Remove user from FedBan list.
    Usage: .unfban <reply/user>
    """
    cmd = message.command
    user_id = None

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(cmd) > 1:
        try:
            user = await client.get_users(cmd[1])
            user_id = user.id
        except:
            await edit_or_reply(message, "<b>❌ Invalid User ID/Username.</b>")
            return

    if not user_id:
        await edit_or_reply(message, "<b>❌ Reply to a user or specify user.</b>")
        return

    await liter.remove_fban(user_id)
    
    # Try unban in current chat
    try:
        await client.unban_chat_member(message.chat.id, user_id)
        text = f"<b>✅ Un-FedBanned:</b> <code>{user_id}</code>"
    except:
        text = f"<b>✅ Removed from DB:</b> <code>{user_id}</code> (Manual unban required here)"

    await edit_or_reply(message, text)


# Watcher: Auto-Ban FedBanned users on arrival
@Client.on_message(filters.group & ~filters.me)
async def fed_watcher(client: Client, message: Message):
    # Only run if we are an admin
    # To save API calls, we could cache our admin status or only check on join events.
    # For now, we check if sender is in DB first (cheap local DB call)
    
    sender = message.from_user
    if not sender:
        return

    fban_status = await liter.get_fban(sender.id)
    if fban_status:
        # User is in FedBan DB. Check if we have permissions to ban.
        try:
            me = await client.get_chat_member(message.chat.id, "me")
            if me.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                if me.privileges and me.privileges.can_restrict_members:
                    await client.ban_chat_member(message.chat.id, sender.id)
                    await message.reply(
                        f"<b>🛡️ FedBan Enforced!</b>\n"
                        f"<b>Banned:</b> {sender.mention}\n"
                        f"<b>Reason:</b> {fban_status.get('reason', 'N/A')}"
                    )
        except Exception:
            pass
