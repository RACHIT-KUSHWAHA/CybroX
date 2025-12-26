# Module: alive.py
#  Legendbot - Advanced Telegram Automation
#  Copyright (C) 2025 Legendbot Organization

import time
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
import logging
from userbot.helpers.misc import modules_help, prefix
from userbot.helpers.managers import edit_or_reply

LOG = logging.getLogger(__name__)

@Client.on_message(filters.command(["alive", "l"], prefix) & filters.me)
async def alive_command(client: Client, message: Message):
    """
    Show that the bot is running. 
    Uses Inline Mode for "Advanced Look" if Assistant is active.
    """
    LOG.info(f"DEBUG: Alive Cmd Entered. Client: {client}, Assistant: {getattr(client, 'assistant', 'Not Set')}")
    # 1. Try Inline "Advanced Look"
    if hasattr(client, "assistant") and client.assistant:
        try:
            bot_username = client.assistant_username
            results = await client.get_inline_bot_results(bot_username, "alive")
            if results and results.results:
                await client.send_inline_bot_result(
                    message.chat.id,
                    results.query_id,
                    results.results[0].id,
                    reply_to_message_id=message.reply_to_message_id
                )
                await message.delete()
                return
            else:
                LOG.info(f"DEBUG: Inline Alive Results Empty for bot {bot_username}")
        except Exception as e:
            # If inline fails, log it and fall back to text
            if "BOT_INLINE_DISABLED" in str(e):
                LOG.warning("Inline mode is disabled for the assistant bot. Please enable it in BotFather.")
            else:
                LOG.error(f"DEBUG: Inline Alive Failed: {e}", exc_info=True)
            pass

    # 2. Text Fallback (Legend Style)
    from userbot.helpers.misc import userbot_version
    await edit_or_reply(
        message,
        f"<b>⚡ 𝗟𝗲𝗴𝗲𝗻𝗱𝗕𝗼𝘁 𝗜𝘀 𝗔𝗹𝗶𝘃𝗲 ⚡</b>\n\n"
        f"<b>👨‍💻 𝗠𝗮𝘀𝘁𝗲𝗿:</b> {client.me.mention}\n"
        f"<b>👾 𝗩𝗲𝗿𝘀𝗶𝗼𝗻:</b> <code>{userbot_version}</code>\n"
        f"<b>🐍 𝗣𝘆𝘁𝗵𝗼𝗻:</b> <code>{platform.python_version()}</code>\n"
        f"<b>🔥 𝗣𝘆𝗿𝗼𝗴𝗿𝗮𝗺:</b> <code>{__import__('pyrogram').__version__}</code>\n"
        f"<b>⏳ 𝗨𝗽𝘁𝗶𝗺𝗲:</b> <code>{get_uptime()}</code>\n\n"
        f"<i>My Master is Pro! 😎</i>"
    )

def get_uptime():
    from userbot import StartTime
    now = time.time()
    delta = now - StartTime
    hours, remainder = divmod(int(delta), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    return f"{days}d {hours}h {minutes}m {seconds}s"
import platform

# Register help information
modules_help["alive"] = {
    "alive": "Check bot status (Inline Button supported)",
    "ping": "Check bot response speed",
    "__category__": "basic"
}

@Client.on_message(filters.command("ping", prefix) & filters.me)
async def ping_cmd(client: Client, message: Message):
    """Check bot speed."""
    start = datetime.now()
    # 1. Edit to "Pong!"
    msg = await edit_or_reply(message, "<b>Pong!</b>")
    end = datetime.now()
    
    # 2. Calculate time taken
    ms = (end - start).microseconds / 1000
    
    # 3. Final Result
    await msg.edit(f"<b>Pong!</b> <code>{ms}ms</code> ⚡")