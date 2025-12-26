#  Legendbot - Advanced Telegram Automation
#  Copyright (C) 2025 Legendbot Organization

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

from userbot.helpers.misc import modules_help, prefix
from userbot.helpers.managers import edit_or_reply

# Emoji mapping for categories
CAT_EMOJIS = {
    "admin": "👮",
    "bot": "🤖",
    "fun": "🎲",
    "misc": "🧩",
    "tools": "🛠️",
    "utils": "🧰",
    "extra": "🔮",
    "core": "⚙️"
}

@Client.on_message(filters.command(["help", "h"], prefix) & filters.me)
async def help_cmd(client: Client, message: Message):
    # 1. Inline Help Menu (The "Advanced Look")
    if len(message.command) == 1:
        if hasattr(client, "assistant") and client.assistant:
            try:
                results = await client.get_inline_bot_results(client.assistant_username, "help")
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
                if "BOT_INLINE_DISABLED" in str(e):
                    # LOG.warning("Inline mode is disabled for the assistant bot. Please enable it in BotFather.")
                    pass
                pass

        # Text Fallback
        text = f"<b>⚡ 𝗟𝗲𝗴𝗲𝗻𝗱𝗕𝗼𝘁 𝗛𝗲𝗹𝗽 𝗠𝗲𝗻𝘂 ⚡</b>\n\n"
        categories = {}
        for module_name, commands in sorted(modules_help.items()):
            category = commands.get("__category__", "misc").lower()
            if category not in categories:
                categories[category] = []
            categories[category].append(module_name)
        
        for category, module_names in sorted(categories.items()):
            emoji = CAT_EMOJIS.get(category, "📂")
            text += f"<b>{emoji} {category.title()}</b>\n"
            text += f"<code>" + "</code>, <code>".join(sorted(module_names)) + "</code>\n\n"
        
        text += f"<b>Total modules:</b> {len(modules_help)}\n"
        text += f"<i>Type <code>{prefix}help [module_name]</code> for more info.</i>"
        await edit_or_reply(message, text)

    # 2. Specific Module Help
    elif message.command[1].lower() in modules_help:
        module_name = message.command[1].lower()
        commands = modules_help[module_name]
        
        text = f"<b>🛠️ Module: {module_name.title()}</b>\n\n"
        for command, description in commands.items():
            if command != "__category__":
                text += f"• <code>{prefix}{command}</code>\n  └ <i>{description}</i>\n\n"
        
        await edit_or_reply(message, text)
    else:
        await edit_or_reply(message, f"<b>❌ Module <code>{message.command[1]}</code> not found!</b>")
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