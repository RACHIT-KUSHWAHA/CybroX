import asyncio
import logging
import json
import os
import time
import motor.motor_asyncio
import redis.asyncio as redis
import aiosqlite
from typing import Optional, Dict, Any, List

# Logging Setup
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("LegendDB")

class UniversalDBManager:
    """
    Legendbot's "Tino ka Mix" Database Manager.
    Orchestrates data persistence across:
    1. Redis (Cache / High Speed)
    2. MongoDB (Cloud / Persistent)
    3. LocalDB (SQLite / Fallback)
    """

    def __init__(self, mongo_uri: str = None, redis_url: str = None, redis_password: str = None, local_db_name: str = "legendbot.db"):
        self.mongo_uri = mongo_uri
        self.redis_url = redis_url
        self.redis_password = redis_password
        self.local_db_name = local_db_name
        
        # Clients
        self.mongo_client = None
        self.mongo_db = None
        self.redis_client = None
        self.local_conn = None
        
        # Status Flags
        self.has_mongo = False
        self.has_redis = False
        self.local_mode = False

        self._lock = asyncio.Lock()

    async def init_database(self):
        """Initializes connections to all available databases."""
        LOG.info("Initializing Legendbot Universal Database...")

        # 1. Initialize LocalDB (Always needed as fallback)
        try:
            self.local_conn = await aiosqlite.connect(self.local_db_name)
            await self.local_conn.execute("PRAGMA journal_mode=WAL;")
            await self.local_conn.execute("""
                CREATE TABLE IF NOT EXISTS kv_store (
                    collection TEXT,
                    key TEXT,
                    value TEXT,
                    PRIMARY KEY (collection, key)
                );
            """)
            await self.local_conn.commit()
            LOG.info("LocalDB (SQLite) Initialized.")
        except Exception as e:
            LOG.critical(f"Failed to init LocalDB: {e}")
            # If local fails, we are in trouble, but let's try others.

        # 2. Initialize MongoDB
        if self.mongo_uri:
            try:
                self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(self.mongo_uri, serverSelectionTimeoutMS=2000)
                # Trigget a command to verify connection
                await self.mongo_client.server_info()
                self.mongo_db = self.mongo_client["Legendbot"]
                self.has_mongo = True
                LOG.info("CloudDB (MongoDB) Connected!")
            except Exception as e:
                LOG.error(f"MongoDB Connection Failed (Falling back to Local): {e}")
                self.local_mode = True
        else:
            LOG.warning("No MONGO_URI provided. Switching to Local Mode.")
            self.local_mode = True

        # 3. Initialize Redis
        if self.redis_url:
            try:
                self.redis_client = redis.from_url(
                    self.redis_url, 
                    password=self.redis_password, 
                    decode_responses=True, 
                    socket_connect_timeout=2
                )
                await self.redis_client.ping()
                self.has_redis = True
                LOG.info("CacheDB (Redis) Connected!")
            except Exception as e:
                LOG.error(f"Redis Connection Failed: {e}")

        # Final Status
        if self.local_mode and not self.has_redis:
            LOG.warning("Running in Pure Local Mode (No Cloud, No Cache). Data is stored in 'legendbot.db'.")
        elif self.has_mongo and self.has_redis:
            LOG.info("Running in High Performance Mode (Cloud + Cache + Local Fallback).")

    async def close(self):
        if self.mongo_client:
            self.mongo_client.close()
        if self.redis_client:
            await self.redis_client.close()
        if self.local_conn:
            await self.local_conn.close()

    # =========================================================================
    # CORE CRUD OPERATIONS (The "Mix")
    # =========================================================================

    async def set(self, collection: str, key: str, value: Any):
        """
        Writes data to all active layers (Write-Through).
        Sequence: Redis -> Mongo -> LocalDB
        """
        json_val = json.dumps(value)

        # 1. Write to Redis (Cache)
        if self.has_redis:
            try:
                # Redis key format: collection:key
                await self.redis_client.set(f"{collection}:{key}", json_val)
            except Exception as e:
                LOG.error(f"Redis Write Failed: {e}")

        # 2. Write to MongoDB (Cloud)
        if self.has_mongo:
            try:
                await self.mongo_db[collection].update_one(
                    {"_id": key}, 
                    {"$set": {"data": value}}, 
                    upsert=True
                )
                # If we successfully wrote to Mongo, we might not strictly need to write to Local,
                # BUT for "Maan lo ... koi db nahi hai", keeping local in sync is good for seamless offline switch.
                # However, syncing *everything* locally might double storage.
                # Requirement implies Fallback. We will write to local ONLY if Cloud fails OR if needed for sync.
                # Use a flag or config for "Full Sync". For now, we write to Local only if Mongo fails for true fallback.
            except Exception as e:
                LOG.error(f"Mongo Write Failed (Writing to LocalDB): {e}")
                await self._write_local(collection, key, json_val)
        else:
            # 3. Write to LocalDB (Fallback)
            await self._write_local(collection, key, json_val)

    async def get(self, collection: str, key: str) -> Optional[Any]:
        """
        Reads data with Read-Aside / Fallback strategy.
        Sequence: Redis -> Mongo -> LocalDB
        """
        # 1. Try Redis
        if self.has_redis:
            try:
                val = await self.redis_client.get(f"{collection}:{key}")
                if val:
                    return json.loads(val)
            except Exception as e:
                LOG.error(f"Redis Read Failed: {e}")

        # 2. Try MongoDB
        if self.has_mongo:
            try:
                doc = await self.mongo_db[collection].find_one({"_id": key})
                if doc:
                    data = doc.get("data")
                    # Populate Cache
                    if self.has_redis:
                         asyncio.create_task(self.redis_client.set(f"{collection}:{key}", json.dumps(data)))
                    return data
            except Exception as e:
                LOG.error(f"Mongo Read Failed (Falling back to LocalDB): {e}")

        # 3. Try LocalDB
        return await self._read_local(collection, key)

    async def delete(self, collection: str, key: str):
        """Deletes from all layers."""
        # Redis
        if self.has_redis:
            try:
                await self.redis_client.delete(f"{collection}:{key}")
            except Exception:
                pass
        
        # Mongo
        if self.has_mongo:
            try:
                await self.mongo_db[collection].delete_one({"_id": key})
            except Exception as e:
                LOG.error(f"Mongo Delete Failed: {e}")
                # Try delete local if mongo failed, just in case it was there?
                await self._delete_local(collection, key)
        else:
            await self._delete_local(collection, key)

    # =========================================================================
    # LOCAL DB HELPERS (SQLite)
    # =========================================================================

    async def _write_local(self, collection: str, key: str, value_json: str):
        async with self._lock:
            try:
                # Upsert sqlite
                await self.local_conn.execute(
                    "INSERT OR REPLACE INTO kv_store (collection, key, value) VALUES (?, ?, ?)",
                    (collection, key, value_json)
                )
                await self.local_conn.commit()
            except Exception as e:
                LOG.error(f"LocalDB Write Failed: {e}")

    async def _read_local(self, collection: str, key: str) -> Optional[Any]:
        async with self._lock:
            try:
                async with self.local_conn.execute(
                    "SELECT value FROM kv_store WHERE collection = ? AND key = ?", 
                    (collection, key)
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return json.loads(row[0])
            except Exception as e:
                LOG.error(f"LocalDB Read Failed: {e}")
        return None

    async def _delete_local(self, collection: str, key: str):
        async with self._lock:
            try:
                await self.local_conn.execute(
                    "DELETE FROM kv_store WHERE collection = ? AND key = ?", 
                    (collection, key)
                )
                await self.local_conn.commit()
            except Exception as e:
                LOG.error(f"LocalDB Delete Failed: {e}")
