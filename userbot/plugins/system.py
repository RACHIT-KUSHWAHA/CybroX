#  CybroX-UserBot - telegram userbot
#  Copyright (C) 2025 CybroX UserBot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

import os
import sys
import time
import platform
import asyncio
import psutil
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import Message
# import git

from userbot.helpers.misc import modules_help, prefix, userbot_version
from userbot.helpers.scripts import edit_or_reply, restart
from userbot.helpers.db import db


@Client.on_message(filters.command("restart", prefix) & filters.me)
async def restart_cmd(client: Client, message: Message):
    start = datetime.now()
    msg = await edit_or_reply(message, "<b>Restarting...</b>")
    
    # Save restart info to database
    db.set("core.updater", "restart_info", {
        "type": "restart",
        "chat_id": message.chat.id,
        "message_id": message.id,
        "time": time.time()
    })
    
    restart()


@Client.on_message(filters.command("update", prefix) & filters.me)
async def update_cmd(client: Client, message: Message):
    await edit_or_reply(message, "<b>❌ Update is disabled in CybroX-Lite.</b>")


@Client.on_message(filters.command(["sysinfo", "neofetch"], prefix) & filters.me)
async def sysinfo_cmd(client: Client, message: Message):
    await message.edit("<b>Collecting system information...</b>")
    
    # CPU info
    cpu_freq = psutil.cpu_freq()
    cpu_freq_text = f"{cpu_freq.current:.2f}MHz" if cpu_freq else "Unknown"
    
    # Memory info
    memory = psutil.virtual_memory()
    
    # Disk info
    disk = psutil.disk_usage("/")
    
    # Uptime
    uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    
    info_text = f"""<b>System Information</b>

<b>CybroX-UserBot:</b> <code>v{userbot_version}</code>
<b>Python:</b> <code>{platform.python_version()}</code>
<b>OS:</b> <code>{platform.system()} {platform.release()}</code>

<b>CPU:</b>
  <b>Cores:</b> <code>{psutil.cpu_count(logical=False)}</code> Physical, <code>{psutil.cpu_count()}</code> Logical
  <b>Usage:</b> <code>{psutil.cpu_percent()}%</code>
  <b>Frequency:</b> <code>{cpu_freq_text}</code>

<b>Memory:</b>
  <b>Total:</b> <code>{memory.total / (1024**3):.2f} GB</code>
  <b>Used:</b> <code>{memory.used / (1024**3):.2f} GB ({memory.percent}%)</code>

<b>Disk:</b>
  <b>Total:</b> <code>{disk.total / (1024**3):.2f} GB</code>
  <b>Used:</b> <code>{disk.used / (1024**3):.2f} GB ({disk.percent}%)</code>

<b>System Uptime:</b> <code>{str(uptime).split('.')[0]}</code>
"""
    await message.edit(info_text)


modules_help["system"] = {
    "restart": "Restart the userbot",
    "update": "Update the userbot from git repository",
    "sysinfo": "Show system information",
    "neofetch": "Alias for sysinfo command",
    "__category__": "system"
}