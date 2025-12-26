import asyncio
import logging
from userbot.database.core import LegendDB
from userbot.helpers import config

# Singleton Database Instance
liter = LegendDB(config.DB_NAME)

class AsyncDatabaseWrapper:
    """
    Wraps LegendDB to provide the legacy get/set/remove interface asynchronous.
    """
    def __init__(self, db_instance: LegendDB):
        self.db = db_instance

    async def get(self, section: str, key: str, default=None):
        # Maps legacy db.get(section, key) to finding a document with _id=key in collection=section
        try:
            doc = await self.db.find_document(section, {"_id": key})
            if doc:
                return doc.get("val", default)
        except Exception:
            pass
        return default

    async def set(self, section: str, key: str, value):
        # Maps legacy db.set(section, key, value) to upserting a document
        # We store as {"_id": key, "val": value}
        data = {"_id": key, "val": value}
        
        # Check if exists to decide add vs update
        existing = await self.db.find_document(section, {"_id": key})
        if existing:
            await self.db.update_document(section, {"_id": key}, {"val": value})
        else:
            await self.db.add_document(section, data)

    async def remove(self, section: str, key: str):
        await self.db.delete_document(section, {"_id": key})

# Instance
db = AsyncDatabaseWrapper(liter)