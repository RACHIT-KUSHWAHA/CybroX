import asyncio
import os
import time
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from userbot.helpers import config

# Configuration
DB_FILENAME = config.DB_NAME
BACKUP_TAG = "#BACKUP_CYBROX"
BACKUP_INTERVAL = 3600  # 60 Minutes

async def restore_db(client: Client):
    """
    Scans Saved Messages for the latest backup and restores it.
    Must be called BEFORE database initialization in main.py.
    """
    if os.path.exists(DB_FILENAME) and os.path.getsize(DB_FILENAME) > 16 * 1024:
        logging.info("Persistence: Local database found and valid. Skipping restore.")
        return

    logging.info("Persistence: Checking for backup in Saved Messages...")
    try:
        # Client must be started!
        async for message in client.search_messages("me", query=BACKUP_TAG, limit=1):
            if message.document:
                logging.info(f"Persistence: Found backup from {message.date}. Downloading...")
                await client.download_media(message, file_name=DB_FILENAME)
                logging.info("Persistence: Database restored successfully.")
                return
        logging.info("Persistence: No backup found. Starting fresh.")
    except Exception as e:
        logging.error(f"Persistence: Restore failed: {e}")

async def backup_db(client: Client):
    """
    Uploads the local database file to Saved Messages.
    """
    if not os.path.exists(DB_FILENAME):
        return
    
    try:
        # We send it as a document to "me" (Saved Messages)
        await client.send_document(
            chat_id="me",
            document=DB_FILENAME,
            caption=f"{BACKUP_TAG}\nTimestamp: {int(time.time())}",
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
        await backup_db(client)

# Manual Backup Command
@Client.on_message(filters.me & filters.command("backup", prefixes="."))
async def force_backup(client: Client, message: Message):
    await message.edit("Creating backup...")
    try:
        await backup_db(client)
        await message.edit(f"Backup uploaded successfully with tag {BACKUP_TAG}.")
    except Exception as e:
        await message.edit(f"Backup failed: {e}")
