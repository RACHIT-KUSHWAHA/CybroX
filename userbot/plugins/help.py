#  CybroX-UserBot - telegram userbot
#  Copyright (C) 2025 CybroX UserBot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

from userbot.helpers.misc import modules_help, prefix
from userbot.helpers.scripts import edit_or_reply


@Client.on_message(filters.command(["help", "h"], prefix) & filters.me)
async def help_cmd(client: Client, message: Message):
    if len(message.command) == 1:
        # Group modules by category
        categories = {}
        for module_name, commands in sorted(modules_help.items()):
            category = getattr(commands, "__category__", "misc")
            if category not in categories:
                categories[category] = []
            categories[category].append(module_name)
        
        text = f"<b>CybroX-UserBot Help</b>\n\n"
        
        # Display modules by category
        for category, module_names in sorted(categories.items()):
            text += f"<b>📂 {category.title()}</b>\n"
            for module_name in sorted(module_names):
                text += f"  <code>{prefix}help {module_name}</code>\n"
            text += "\n"
        
        text += f"<b>Total modules:</b> {len(modules_help)}"
        
        await edit_or_reply(message, text)
    elif message.command[1].lower() in modules_help:
        module_name = message.command[1].lower()
        commands = modules_help[module_name]
        
        text = f"<b>Help for {module_name} module</b>\n\n"
        for command, description in commands.items():
            if command != "__category__":  # Skip category indicator
                text += f"<code>{prefix}{command}</code>: {description}\n"
        
        await edit_or_reply(message, text)
    else:
        await edit_or_reply(message, f"<b>Module {message.command[1]} not found!</b>")
        await asyncio.sleep(3)
        await message.delete()


@Client.on_message(filters.command("modules", prefix) & filters.me)
async def modules_cmd(client: Client, message: Message):
    text = "<b>Installed modules:</b>\n\n"
    text += "\n".join([f"• <code>{module}</code>" for module in sorted(modules_help.keys())])
    text += f"\n\n<b>Total:</b> {len(modules_help)} modules"
    await edit_or_reply(message, text)


modules_help["help"] = {
    "help [module]": "Get help for a specific module or list all modules",
    "h [module]": "Alias for help command",
    "modules": "Show list of all installed modules",
    "__category__": "core"
}