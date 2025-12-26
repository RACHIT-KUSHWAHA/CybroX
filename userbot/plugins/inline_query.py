from pyrogram import Client, filters, enums
from pyrogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    InlineQueryResultArticle, 
    InputTextMessageContent,
    InlineQueryResultPhoto
)
from userbot.core.session import app
from userbot.helpers import config

# Rebranding
# We attach these handlers to the ASSISTANT bot.
# But since this file is loaded by the USERBOT (app), we need to manually register handlers 
# to app.assistant if we want them to run on the assistant. 
# OR, more cleanly, we check if app.assistant exists and add_handler.

if app.assistant:
    @app.assistant.on_inline_query()
    async def inline_handler(client, query):
        text = query.query.strip()
        results = []

        # 1. Alive / Help Button
        if text == "alive":
            results.append(
                InlineQueryResultPhoto(
                    title="Alive",
                    photo_url=config.ALIVE_PIC if hasattr(config, "ALIVE_PIC") and config.ALIVE_PIC else "https://telegra.ph/file/a7585093557cfc7075253.jpg",
                    caption=f"<b>Legendbot is Online</b>\n\n<b>Version:</b> 2.0 (Architect)\n<b>Status:</b> Operational",
                    description="Check Bot Status",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Legend Support", url="https://t.me/LegendbotSupport")],
                        [InlineKeyboardButton("Help Menu", callback_data="help_menu")]
                    ])
                )
            )
        
        # 2. Help Menu
        elif text == "help":
             results.append(
                InlineQueryResultArticle(
                    title="Legendbot Help",
                    input_message_content=InputTextMessageContent("<b>Legendbot Help Menu</b>\nSelect a module below:"),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("General", callback_data="help_general"), InlineKeyboardButton("Tools", callback_data="help_tools")],
                        [InlineKeyboardButton("Close", callback_data="close")]
                    ])
                )
             )

        await client.answer_inline_query(query.id, results=results, cache_time=0)

    @app.assistant.on_callback_query()
    async def callback_handler(client, callback):
        data = callback.data
        if data == "close":
            await callback.message.delete()
        elif data == "help_menu":
            await callback.edit_message_text(
                "<b>Legendbot Help Menu</b>\nSelect a module:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("General", callback_data="help_general"), InlineKeyboardButton("Tools", callback_data="help_tools")],
                    [InlineKeyboardButton("Close", callback_data="close")]
                ])
            )
        elif data == "help_general":
             await callback.edit_message_text(
                "<b>General Commands:</b>\n.alive - Check status\n.ping - Check latency",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="help_menu")]])
            )
        elif data == "help_tools":
             await callback.edit_message_text(
                "<b>Tools:</b>\n.purge - Delete messages\n.spam - Spam text",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="help_menu")]])
            )
