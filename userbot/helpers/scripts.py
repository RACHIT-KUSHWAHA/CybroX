#  Legendbot-UserBot - telegram userbot
#  Copyright (C) 2025 Legendbot UserBot Organization
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


def restart():
    """Restart the bot"""
    os.execl(sys.executable, sys.executable, "main.py")