import asyncio
import logging
from userbot.database.core import db as liter
from userbot.helpers import config

# Singleton Database Instance
# We use the initialized instance from userbot.database.core
# liter = LegendDB(local_db_name=config.DB_NAME) <- This was creating a new uninitialized instance

# Export as 'db' to maintain compatibility if plugins import 'db' from here
db = liter

# Monkey Patching is likely not needed if we use the core instance which is properly initialized
# But if LegendDB class is missing methods, we might need to patch the class or the instance.
# LegendDB class in userbot/database/core.py ALREADY has add_fban, remove_fban, get_fban.
# So we don't need to patch it here.
