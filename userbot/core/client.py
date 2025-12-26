import logging
import time
import importlib
import sys
import glob
from pathlib import Path

from pyrogram import Client, errors, enums
from pyrogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    InlineQueryResultArticle, 
    InputTextMessageContent
)

from userbot.helpers import config
from userbot.database.core import db 

# Logging
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("Legendbot")

class Legendbot(Client):
    """
    Object-Oriented Legendbot Core.
    Extends Pyrogram Client to include built-in Database management,
    Helper invocation, and Assistant Bot orchestration.
    """
    def __init__(self):
        # Initialize Helper/Assistant Bot if token provided
        self.assistant = None
        self.assistant_username = None
        if config.BOT_TOKEN:
            self.assistant = Client(
                "LegendHelper",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                bot_token=config.BOT_TOKEN,
                in_memory=True
            )

        # Standard Client Init
        super().__init__(
            "legendbot",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=config.SESSION_STRING,
            plugins=dict(root="userbot.plugins"),
            parse_mode=enums.ParseMode.HTML
        )
        
        # Bind Database to Instance
        self.db = db

    async def start(self):
        """
        Lifecycle Method: Start
        1. Init Database
        2. Start Assistant (if any)
        3. Connect Userbot
        4. Load Plugins
        """
        LOG.info("Legendbot: Initializing Database...")
        await self.db.init_database()
        
        if self.assistant:
            LOG.info("Legendbot: Starting Assistant Bot...")
            await self.assistant.start()
            me = await self.assistant.get_me()
            self.assistant_username = me.username
            LOG.info(f"Legendbot: Assistant Started as @{me.username}")

        LOG.info("Legendbot: Connecting to Telegram...")
        await super().start()
        
        me = await self.get_me()
        LOG.info(f"Legendbot: Started as {me.first_name} (ID: {me.id})")
        
        # Post-Start hook: Update restart status if needed
        # (This logic is usually in main.py, but can be here too)

    async def stop(self, *args):
        """Graceful Shutdown"""
        if self.assistant:
            await self.assistant.stop()
        await super().stop()
        await self.db.close()
        LOG.info("Legendbot: Offline.")

    def load_plugins_manual(self):
        """
        Manual plugin loader if we don't want to use Pyrogram's 'plugins' dict
        or if we need custom logic (like excluding modules based on DB flags).
        Currently relying on super().__init__(plugins=...) but this is here for future expansion.
        """
        pass
    
    # helper for inline queries ("Help Button" requirement)
    async def get_inline_bot_results(self, query=""):
        """
        Fetch results from the assistant bot.
        Wrapper for client.get_inline_bot_results(self.assistant_username, query)
        """
        if not self.assistant_username:
            return None
        return await super().get_inline_bot_results(self.assistant_username, query)

    # Re-exporting helpers as methods
    # from userbot.helpers.managers import edit_or_reply 
    # ^ We can bind this dynamically or just usage imports in plugins.
