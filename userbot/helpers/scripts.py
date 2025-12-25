#  CybroX-UserBot - telegram userbot
#  Copyright (C) 2025 CybroX UserBot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

import asyncio
import os
import sys
import traceback
from typing import Union
from pyrogram.types import Message


async def edit_or_reply(message: Message, text: str, **kwargs):
    """Edit message if from self, reply otherwise"""
    if message.from_user and message.from_user.is_self:
        return await message.edit(text, **kwargs)
    else:
        return await message.reply(text, **kwargs)


async def with_reply(message: Message) -> Union[Message, bool]:
    """Check if message has reply and return it"""
    reply = message.reply_to_message
    if not reply:
        await message.edit("<b>Reply to message is required</b>")
        await asyncio.sleep(3)
        await message.delete()
        return False
    return reply


def restart():
    """Restart the bot"""
    os.execl(sys.executable, sys.executable, "main.py")