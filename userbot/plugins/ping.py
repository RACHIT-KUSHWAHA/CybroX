# Module: ping.py
#  CybroX-UserBot - telegram userbot
#  Copyright (C) 2025 CybroX UserBot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

import time
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message

from userbot.helpers.misc import modules_help, prefix
from userbot.helpers.scripts import edit_or_reply


@Client.on_message(filters.command(["ping", "p"], prefix) & filters.me)
async def ping_command(client: Client, message: Message):
    """Ping command to check response time"""
    start = datetime.now()
    msg = await edit_or_reply(message, "<b>Pinging...</b>")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await msg.edit(f"<b>🏓 Pong!</b>\n<code>{ms:.2f}ms</code>")


@Client.on_message(filters.command("alive", prefix) & filters.me)
async def alive_command(client: Client, message: Message):
    """Show that the bot is running"""
    from userbot.helpers.misc import userbot_version
    
    await message.edit(
        f"<b>🔥 CybroX-UserBot is alive!</b>\n\n"
        f"<b>Version:</b> <code>{userbot_version}</code>\n"
        f"<b>Pyrogram:</b> <code>{__import__('pyrogram').__version__}</code>\n"
        f"<b>Prefix:</b> <code>{prefix}</code>"
    )


# Register help information
modules_help["ping"] = {
    "ping": "Check bot response time",
    "p": "Alias for ping command",
    "alive": "Show that the bot is running",
    "__category__": "basic"
}