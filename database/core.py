
import asyncio
import os
import time
import logging
from pyrogram import Client
from userbot.helpers import config

# Constants
# We use the config.DB_NAME if available, else default
DB_FILENAME = getattr(config, "DB_NAME", "cybrox.db") 
BACKUP_TAG = "#BACKUP_CYBROX"
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
        # Deleting previous backups could be good to save space, but risky if upload fails.
        # We'll just append for now.
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
