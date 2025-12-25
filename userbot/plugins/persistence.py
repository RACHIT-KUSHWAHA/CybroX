
from pyrogram import Client, filters
from pyrogram.types import Message
from userbot.database.core import backup_database, BACKUP_TAG

# Manual Backup Command
@Client.on_message(filters.me & filters.command("backup", prefixes="."))
async def force_backup(client: Client, message: Message):
    """
    Manually trigger the database backup to Saved Messages.
    Usage: .backup
    """
    await message.edit("Creating backup...")
    try:
        await backup_database(client)
        await message.edit(f"Backup uploaded successfully with tag {BACKUP_TAG}.")
    except Exception as e:
        await message.edit(f"Backup failed: {e}")
