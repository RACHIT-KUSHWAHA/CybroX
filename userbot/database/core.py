import logging
import os
import time
from pyrogram import Client
from userbot.helpers import config
# Import the new Universal Manager
from userbot.database.universal import UniversalDBManager

# Rebranding: Rename class to LegendDB
class LegendDB(UniversalDBManager):
    """
    Wrapper for UniversalDBManager to maintain backward compatibility
    while switching to the new Legendbot capabilities.
    """
    pass

# Initialize the Global Database Instance
# We rely on config for URIs
# Note: These env vars should be added to config.py if not present
MONGO_URI = getattr(config, "MONGO_URI", None)
REDIS_URL = getattr(config, "REDIS_URL", None)
REDIS_PASSWORD = getattr(config, "REDIS_PASSWORD", None)

db = LegendDB(mongo_uri=MONGO_URI, redis_url=REDIS_URL, redis_password=REDIS_PASSWORD)

# -----------------------------------------------------------
# Federation / Anti-Spam Methods (Phase 8.2) - Adapted for UniversalDB
# -----------------------------------------------------------
# These methods now use the `db.set` and `db.get` abstraction
# which handles the Redis -> Mongo -> Local fallback automatically.

async def add_fban(user_id: int, reason: str, admin_id: int):
    """Add a user to the global ban list."""
    await db.set("fban_list", str(user_id), {"reason": reason, "admin": admin_id, "date": int(time.time())})

async def remove_fban(user_id: int):
    """Remove a user from the global ban list."""
    await db.delete("fban_list", str(user_id))

async def get_fban(user_id: int):
    """Check if user is fbanned. Returns dict or None."""
    return await db.get("fban_list", str(user_id))


# Constants
DB_FILENAME = getattr(config, "DB_NAME", "legendbot.db") 
BACKUP_TAG = "#BACKUP_LEGENDBOT"
BACKUP_INTERVAL = 3600  # 60 Minutes

async def restore_database(client: Client):
    """
    Scans Saved Messages for the latest backup and restores it.
    Must be called BEFORE database initialization in main.py.
    """
    if os.path.exists(DB_FILENAME) and os.path.getsize(DB_FILENAME) > 16 * 1024:
        logging.info("Persistence: Local database found and valid. Skipping restore.")
        return

    logging.info("Persistence: Checking for backup in Saved Messages...")
    try:
        # Search for the specific tag in Saved Messages ("me")
        # limit=1 gets the most recent one
        found_backup = False
        async for message in client.search_messages("me", query=BACKUP_TAG, limit=5):
            if message.document and message.document.file_name == DB_FILENAME:
                logging.info(f"Persistence: Found backup from {message.date}. Downloading...")
                await client.download_media(message, file_name=DB_FILENAME)
                logging.info("Persistence: Database restored successfully.")
                found_backup = True
                break
        
        if not found_backup:
            logging.info("Persistence: No backup found. Starting fresh.")
            
    except Exception as e:
        logging.error(f"Persistence: Restore failed: {e}")

async def backup_database(client: Client):
    """
    Uploads the local database file to Saved Messages.
    """
    if not os.path.exists(DB_FILENAME):
        return
    
    try:
        # We send it as a document to "me" (Saved Messages)
        timestamp = int(time.time())
        caption = f"{BACKUP_TAG}\nTimestamp: {timestamp}\nAuto-Backup"
        
        await client.send_document(
            chat_id="me",
            document=DB_FILENAME,
            caption=caption,
            force_document=True
        )
        logging.info("Persistence: Backup uploaded successfully.")
    except Exception as e:
        logging.error(f"Persistence: Backup failed: {e}")

async def start_backup_loop(client: Client):
    """
    Starts the periodic backup task.
    """
    logging.info("Persistence: Backup loop started.")
    while True:
        await asyncio.sleep(BACKUP_INTERVAL)
        await backup_database(client)


