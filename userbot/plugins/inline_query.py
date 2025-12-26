import re
import math
import time
import random
import platform
from pyrogram import Client, filters, enums, __version__ as pyro_version
from pyrogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    InlineQueryResultArticle, 
    InputTextMessageContent,
    InlineQueryResultPhoto,
    LinkPreviewOptions
)
from userbot import StartTime
from userbot.core.session import app
from userbot.helpers import config
from userbot.helpers.misc import modules_help, userbot_version, python_version

# Constants
GRP_INFO = {
    "admin": [],
    "bot": [],
    "fun": [],
    "misc": [],
    "tools": [],
    "utils": [],
    "extra": []
}

# Emoji mapping for categories
CAT_EMOJIS = {
    "admin": "👮",
    "bot": "🤖",
    "fun": "🎲",
    "misc": "🧩",
    "tools": "🛠️",
    "utils": "🧰",
    "extra": "🔮"
}

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time

def categorize_modules():
    """Organize modules into categories dynamically."""
    # Reset lists
    for key in GRP_INFO:
        GRP_INFO[key] = []
    
    # Check if modules_help is populated
    if not modules_help:
        return

    for module, help_dict in modules_help.items():
        cat = help_dict.get("__category__", "misc").lower()
        if cat not in GRP_INFO:
            cat = "extra" # Fallback
        
        # Avoid duplicates
        if module not in GRP_INFO[cat]:
            GRP_INFO[cat].append(module)

def get_thumb(name=None, url=None):
    """Helper to get thumbnail URL."""
    if url:
        return url
    # Default fallback
    return "https://downloads.codinginfinite.com/wp-content/uploads/2022/11/banner-28-1.png"

def main_menu_buttons():
    """Generate the main menu buttons similar to CatUserBot."""
    categorize_modules()
    
    # Calculate counts
    counts = {k: len(v) for k, v in GRP_INFO.items()}
    
    buttons = [
        [
            InlineKeyboardButton(f"{CAT_EMOJIS['admin']} Admin ({counts['admin']})", callback_data="cat_admin"),
            InlineKeyboardButton(f"{CAT_EMOJIS['bot']} Bot ({counts['bot']})", callback_data="cat_bot"),
            InlineKeyboardButton(f"{CAT_EMOJIS['fun']} Fun ({counts['fun']})", callback_data="cat_fun"),
        ],
        [
            InlineKeyboardButton(f"{CAT_EMOJIS['misc']} Misc ({counts['misc']})", callback_data="cat_misc"),
            InlineKeyboardButton(f"{CAT_EMOJIS['tools']} Tools ({counts['tools']})", callback_data="cat_tools"),
            InlineKeyboardButton(f"{CAT_EMOJIS['utils']} Utils ({counts['utils']})", callback_data="cat_utils"),
        ],
        [
            InlineKeyboardButton(f"{CAT_EMOJIS['extra']} Extra ({counts['extra']})", callback_data="cat_extra"),
        ],
        [
            InlineKeyboardButton("ℹ️ About", callback_data="check"),
            InlineKeyboardButton("📊 Stats", callback_data="stats"),
            InlineKeyboardButton("🔒 Close", callback_data="close"),
        ],
    ]
    return buttons

class InlineBuilder:
    @staticmethod
    def article(title, text, description=None, thumb=None, buttons=None, url=None):
        return InlineQueryResultArticle(
            title=title,
            description=description,
            thumb_url=get_thumb(url=thumb),
            input_message_content=InputTextMessageContent(
                text, 
                link_preview_options=LinkPreviewOptions(is_disabled=False)
            ),
            reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
        )

    @staticmethod
    def photo(title, photo_url, caption, description=None, buttons=None):
        return InlineQueryResultPhoto(
            title=title,
            description=description,
            photo_url=photo_url,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
        )

if app.assistant:
    @app.assistant.on_inline_query()
    async def inline_handler(client, query):
        text = query.query.strip()
        results = []
        
        # 1. Alive / Stats
        if text in ["alive", "stats"]:
            uptime = get_readable_time(int(time.time() - StartTime))
            start = time.time()
            # Simulate ping (since we can't easily ping from inline)
            end = time.time()
            ms = (end - start) * 1000
            
            buttons = [
                [
                    InlineKeyboardButton("Stats", callback_data="stats"),
                    InlineKeyboardButton("Repo", url="https://github.com/LegendBot/LegendBot")
                ],
                [InlineKeyboardButton("🗑️ Close", callback_data="close")]
            ]
            
            alive_text = (
                f"<b>⚡ 𝗟𝗲𝗴𝗲𝗻𝗱𝗕𝗼𝘁 𝗜𝘀 𝗔𝗹𝗶𝘃𝗲 ⚡</b>\n\n"
                f"<b>👨‍💻 𝗠𝗮𝘀𝘁𝗲𝗿:</b> {app.me.mention}\n"
                f"<b>👾 𝗩𝗲𝗿𝘀𝗶𝗼𝗻:</b> <code>{userbot_version}</code>\n"
                f"<b>🐍 𝗣𝘆𝘁𝗵𝗼𝗻:</b> <code>{python_version}</code>\n"
                f"<b>🔥 𝗣𝘆𝗿𝗼𝗴𝗿𝗮𝗺:</b> <code>{pyro_version}</code>\n"
                f"<b>⏳ 𝗨𝗽𝘁𝗶𝗺𝗲:</b> <code>{uptime}</code>\n"
                f"<b>📶 𝗣𝗶𝗻𝗴:</b> <code>{ms:.2f}ms</code>\n\n"
                f"<i>My Master is Pro! 😎</i>"
            )
            
            results.append(
                InlineBuilder.photo(
                    title="LegendBot Alive",
                    description="Check Bot Status",
                    photo_url=config.ALIVE_PIC if hasattr(config, "ALIVE_PIC") and config.ALIVE_PIC else "https://downloads.codinginfinite.com/wp-content/uploads/2022/11/banner-28-1.png",
                    caption=alive_text,
                    buttons=buttons
                )
            )

        # 2. Help Menu
        elif text == "help":
             help_text = (
                 f"<b>⚡ 𝗟𝗲𝗴𝗲𝗻𝗱𝗕𝗼𝘁 𝗛𝗲𝗹𝗽 𝗠𝗲𝗻𝘂 ⚡</b>\n\n"
                 f"<b>Hello! I am LegendBot Helper.</b>\n"
                 f"I am here to help you manage your LegendBot.\n\n"
                 f"<b>📂 Modules:</b> {len(modules_help)}\n"
                 f"<b>Select a category below to see available commands.</b>"
             )
             results.append(
                InlineBuilder.article(
                    title="Help Menu",
                    text=help_text,
                    description="Open the interactive help menu.",
                    thumb="https://telegra.ph/file/a7585093557cfc7075253.jpg",
                    buttons=main_menu_buttons()
                )
             )

        # 3. Repo / Source
        elif text == "repo":
            buttons = [
                [InlineKeyboardButton("Source Code", url="https://github.com/LegendBot/LegendBot")]
            ]
            results.append(
                InlineBuilder.article(
                    title="LegendBot Source",
                    text="<b>LegendBot is Open Source.</b>\n\nCheck out the repo below.",
                    description="Get the source code",
                    buttons=buttons
                )
            )
        
        # 4. Fallback search (Empty query or unrecognized)
        # We can implement specific search if needed, but for now we leave it empty
        # to prevent errors.

        await client.answer_inline_query(query.id, results=results, cache_time=0)

    @app.assistant.on_callback_query()
    async def callback_handler(client, callback):
        data = callback.data
        categorize_modules() # Ensure up to date

        if data == "close":
            if callback.message:
                await callback.message.delete()
            else:
                # If it's an inline message, we can't delete it, but we can edit it to be empty/closed
                await client.edit_inline_text(callback.inline_message_id, "<b>🗑️ Menu Closed</b>")

        elif data == "help_menu" or data == "mainmenu":
            if callback.message:
                await callback.edit_message_text(
                    f"<b>⚡ 𝗟𝗲𝗴𝗲𝗻𝗱𝗕𝗼𝘁 𝗛𝗲𝗹𝗽 𝗠𝗲𝗻𝘂 ⚡</b>\n\n"
                    f"<b>Hello! I am LegendBot Helper.</b>\n"
                    f"I am here to help you manage your LegendBot.\n\n"
                    f"<b>📂 Modules:</b> {len(modules_help)}\n"
                    f"<b>Select a category below to see available commands.</b>",
                    reply_markup=InlineKeyboardMarkup(main_menu_buttons())
                )
            else:
                 await client.edit_inline_text(
                    callback.inline_message_id,
                    f"<b>⚡ 𝗟𝗲𝗴𝗲𝗻𝗱𝗕𝗼𝘁 𝗛𝗲𝗹𝗽 𝗠𝗲𝗻𝘂 ⚡</b>\n\n"
                    f"<b>Hello! I am LegendBot Helper.</b>\n"
                    f"I am here to help you manage your LegendBot.\n\n"
                    f"<b>📂 Modules:</b> {len(modules_help)}\n"
                    f"<b>Select a category below to see available commands.</b>",
                    reply_markup=InlineKeyboardMarkup(main_menu_buttons())
                )
        
        elif data == "check":
            await callback.answer("LegendBot - The Most Powerful Userbot", show_alert=True)
            
        elif data == "stats":
             await callback.answer("Stats feature coming soon!", show_alert=True)

        elif data.startswith("cat_"):
            category = data.split("_")[1]
            modules = sorted(GRP_INFO.get(category, []))
            
            buttons = []
            current_row = []
            for mod in modules:
                # Using emoji if possible, for now just name
                dummy_emoji = "🔹"
                current_row.append(InlineKeyboardButton(f"{dummy_emoji} {mod.title()}", callback_data=f"mod_{mod}"))
                if len(current_row) == 2: # 2 columns
                    buttons.append(current_row)
                    current_row = []
            if current_row:
                buttons.append(current_row)
            
            buttons.append([InlineKeyboardButton("🔙 Back", callback_data="help_menu")])
            
            if callback.message:
                await callback.edit_message_text(
                    f"<b>📂 Category: {category.title()}</b>\n\nSelect a module to see commands:",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            else:
                await client.edit_inline_text(
                    callback.inline_message_id,
                    f"<b>📂 Category: {category.title()}</b>\n\nSelect a module to see commands:",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

        elif data.startswith("mod_"):
            module = data.split("_")[1]
            if module in modules_help:
                 commands = modules_help[module]
                 text = f"<b>🛠️ Module: {module.title()}</b>\n\n"
                 
                 # Basic command listing
                 for command, description in commands.items():
                     if command != "__category__":
                         text += f"• <code>.{command}</code>\n  └ <i>{description}</i>\n\n"
                 
                 cat = commands.get("__category__", "misc")
                 buttons = [
                     [InlineKeyboardButton("🔙 Back", callback_data=f"cat_{cat}"), InlineKeyboardButton("🏠 Main Menu", callback_data="help_menu")]
                 ]
                 
                 if callback.message:
                     await callback.edit_message_text(
                        text,
                        reply_markup=InlineKeyboardMarkup(buttons)
                     )
                 else:
                     await client.edit_inline_text(
                        callback.inline_message_id,
                        text,
                        reply_markup=InlineKeyboardMarkup(buttons)
                     )
