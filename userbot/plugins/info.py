#  CybroX-UserBot - telegram userbot
#  Copyright (C) 2025 CybroX UserBot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import datetime
import platform
import sys
from pyrogram import Client, filters
from pyrogram.types import Message

from userbot.helpers.misc import modules_help, prefix, python_version, userbot_version


@Client.on_message(filters.command(["about", "info"], prefix) & filters.me)
async def about(client: Client, message: Message):
    await message.edit(
        f"<b>CybroX-UserBot</b>\n\n"
        f"<b>• Version:</b> <code>{userbot_version}</code>\n"
        f"<b>• Python:</b> <code>{python_version}</code>\n"
        f"<b>• Pyrogram:</b> <code>{'.'.join(str(x) for x in client.pyrogram_version)}</code>\n"
        f"<b>• Platform:</b> <code>{sys.platform}</code>\n"
        f"<b>• System:</b> <code>{platform.version()}</code>\n\n"
        f"<b>• Repository:</b> <a href='https://github.com/YourUsername/CybroX-UserBot'>GitHub</a>\n"
        f"<b>• Channel:</b> <a href='https://t.me/YourChannel'>Telegram</a>"
    )


@Client.on_message(filters.command("help", prefix) & filters.me)
async def help_command(client: Client, message: Message):
    if len(message.command) > 1:
        module_name = message.command[1].lower()
        if module_name in modules_help:
            await message.edit(
                f"<b>Help for {module_name} module:</b>\n\n"
                + "\n".join(
                    f"<code>{prefix}{command}</code>: {description}"
                    for command, description in modules_help[module_name].items()
                )
            )
        else:
            await message.edit(f"<b>Module {module_name} not found!</b>")
    else:
        await message.edit(
            f"<b>CybroX UserBot Help</b>\n\n"
            f"<b>Available Modules:</b>\n"
            + "\n".join(f"• <code>{module}</code>" for module in sorted(modules_help.keys()))
            + f"\n\nUse <code>{prefix}help [module]</code> to get help for a specific module."
        )


modules_help["info"] = {
    "about": "Show information about userbot",
    "info": "Show information about userbot",
    "help": "Show this help message",
    "help [module]": "Show help for a specific module",
}