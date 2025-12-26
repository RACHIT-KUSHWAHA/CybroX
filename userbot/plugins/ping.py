# Module: alive.py
#  Legendbot - Advanced Telegram Automation
#  Copyright (C) 2025 Legendbot Organization

import time
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from userbot.helpers.misc import modules_help, prefix
from userbot.helpers.managers import edit_or_reply

@Client.on_message(filters.command(["alive", "l"], prefix) & filters.me)
async def alive_command(client: Client, message: Message):
    """
    Show that the bot is running. 
    Uses Inline Mode for "Advanced Look" if Assistant is active.
    """
    # 1. Try Inline "Advanced Look"
    if hasattr(client, "assistant") and client.assistant:
        try:
            bot_username = client.assistant_username
            results = await client.get_inline_bot_results(query="alive")
            if results and results.results:
                await client.send_inline_bot_result(
                    message.chat.id,
                    results.query_id,
                    results.results[0].id,
                    reply_to_message_id=message.reply_to_message_id
                )
                await message.delete()
                return
        except Exception as e:
            # If inline fails (e.g. timeout, or not allowed in chat), fall back to text
            pass

    # 2. Text Fallback
    from userbot.helpers.misc import userbot_version
    await edit_or_reply(
        message,
        f"<b>🔥 Legendbot is Alive!</b>\n\n"
        f"<b>Version:</b> <code>1.0 (Legend)</code>\n"
        f"<b>Pyrogram:</b> <code>{__import__('pyrogram').__version__}</code>\n"
        f"<b>Mode:</b> <code>Hybrid (Mongo + Redis + SQLite)</code>"
    )

# Register help information
modules_help["alive"] = {
    "alive": "Check bot status (Inline Button supported)",
    "__category__": "basic"
}