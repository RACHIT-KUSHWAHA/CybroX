import aiosqlite
import asyncio
import json
import logging
import uuid

class CybroDB:
    """
    Aiosqlite wrapper that mimics MongoDB's document store behavior.
    Optimized for 'Lite Plan' zero-cost hosting.
    """
    def __init__(self, db_name="cybrox.db"):
        self.db_name = db_name
        self.conn = None
        self._lock = asyncio.Lock()

    async def init(self):
        """Initialize the database connection and schema."""
        self.conn = await aiosqlite.connect(self.db_name)
        
        # Enable Write-Ahead Logging for concurrency
        await self.conn.execute("PRAGMA journal_mode=WAL;")
        
        # Create the Generic Key-Value Store table
        # collection: replicates MongoDB collection name
        # key: generic unique identifier (usually UUID or specific ID)
        # value: JSON serialized data
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS kv_store (
                collection TEXT,
                key TEXT,
                value TEXT,
                PRIMARY KEY (collection, key)
            );
        """)
        
        # Enable FTS5 for efficient message searching
        # contentless_delete=1 allows deleting rows without rebuilding the whole index (available in newer SQLite versions)
        # unindexed=timestamp allows storing it but not indexing it (faster inserts)
        await self.conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS fts_messages USING fts5(
                message_id, 
                chat_id, 
                text, 
                timestamp UNINDEXED, 
                sender_id UNINDEXED, 
                tokenize='porter'
            );
        """)
        await self.conn.commit()
        logging.info(f"CybroDB initialized with WAL mode on {self.db_name}")

    async def close(self):
        if self.conn:
            await self.conn.close()

    async def add_document(self, collection: str, data: dict):
        """
        Mimics insert_one.
        If '_id' is missing, generates a UUID.
        """
        async with self._lock:
            if "_id" not in data:
                data["_id"] = str(uuid.uuid4())
            
            key = str(data["_id"])
            # Convert dictionary to JSON string
            value = json.dumps(data)
            
            try:
                await self.conn.execute(
                    "INSERT INTO kv_store (collection, key, value) VALUES (?, ?, ?)",
                    (collection, key, value)
                )
                await self.conn.commit()
                return key
            except aiosqlite.IntegrityError:
                logging.error(f"Document with key {key} already exists in {collection}")
                return None

    async def find_document(self, collection: str, query_dict: dict):
        """
        Mimics find_one.
        Fetches all rows for the collection and filters in Python.
        """
        async with self._lock:
            async with self.conn.execute(
                "SELECT value FROM kv_store WHERE collection = ?", (collection,)
            ) as cursor:
                async for row in cursor:
                    try:
                        # Convert JSON string back to dictionary
                        doc = json.loads(row[0])
                        
                        # Simple match: all keys in query_dict must match doc
                        match = True
                        for k, v in query_dict.items():
                            if doc.get(k) != v:
                                match = False
                                break
                        if match:
                            return doc
                    except json.JSONDecodeError:
                        continue
        return None

    async def update_document(self, collection: str, query_dict: dict, update_data: dict):
        """
        Mimics update_one.
        First finds the document, merges changes, and updates the row.
        """
        # Find the document first
        target_doc = await self.find_document(collection, query_dict)
        
        if not target_doc:
            return None

        # Merge update_data
        # Support "$set" operator if passed (common in Mongo)
        if "$set" in update_data:
            target_doc.update(update_data["$set"])
        else:
            target_doc.update(update_data)

        key = str(target_doc["_id"])
        new_value = json.dumps(target_doc)

        async with self._lock:
            await self.conn.execute(
                "UPDATE kv_store SET value = ? WHERE collection = ? AND key = ?",
                (new_value, collection, key)
            )
            await self.conn.commit()
        
        return target_doc

    async def delete_document(self, collection: str, query_dict: dict):
        """
        Mimics delete_one.
        """
        target_doc = await self.find_document(collection, query_dict)
        if not target_doc:
            return 0
            
        key = str(target_doc["_id"])
        
        async with self._lock:
            await self.conn.execute(
                "DELETE FROM kv_store WHERE collection = ? AND key = ?",
                (collection, key)
            )
            await self.conn.commit()
        return 1

    async def insert_message_index(self, mid, cid, text, ts, sid):
        """Insert a message into the FTS index for rapid searching."""
        async with self._lock:
            # Check if message already exists to avoid duplicates (FTS tables don't have standard primary keys in the same way)
            # We delete older version if it exists to support edits
            await self.conn.execute(
                "DELETE FROM fts_messages WHERE message_id = ? AND chat_id = ?",
                (mid, cid)
            )
            await self.conn.execute(
                "INSERT INTO fts_messages (message_id, chat_id, text, timestamp, sender_id) VALUES (?, ?, ?, ?, ?)",
                (mid, cid, text, ts, sid)
            )
            await self.conn.commit()

    async def search_messages(self, query: str, limit: int = 20):
        """Search the FTS index using BM25 ranking."""
        results = []
        async with self._lock:
            async with self.conn.execute(
                """
                SELECT message_id, chat_id, text, timestamp, sender_id 
                FROM fts_messages 
                WHERE fts_messages MATCH ? 
                ORDER BY rank 
                LIMIT ?
                """,
                (query, limit)
            ) as cursor:
                async for row in cursor:
                    results.append({
                        "message_id": row[0],
                        "chat_id": row[1],
                        "text": row[2],
                        "timestamp": row[3],
                        "sender_id": row[4]
                    })
        return results

    async def wipe_fts_index(self):
        """Clear all indexed messages (for privacy or reset)."""
        async with self._lock:
            await self.conn.execute("DELETE FROM fts_messages")
            await self.conn.commit()

    # -----------------------------------------------------------
    # KV Store Convenience Wrappers
    # -----------------------------------------------------------
    async def set(self, collection: str, key: str, value: dict):
        """Wrapper for add_document (upsert logic needed ideally, but add_document mimics insert)."""
        # We'll try to add, if it fails (exists), we update.
        existing = await self.find_document(collection, {"_id": key})
        if existing:
            return await self.update_document(collection, {"_id": key}, value)
        
        # Ensure _id is set to key
        value["_id"] = key
        return await self.add_document(collection, value)

    async def get(self, collection: str, key: str):
        """Wrapper for find_document."""
        return await self.find_document(collection, {"_id": key})

    async def delete(self, collection: str, key: str):
        """Wrapper for delete_document."""
        return await self.delete_document(collection, {"_id": key})

    # -----------------------------------------------------------
    # Federation / Anti-Spam Methods (Phase 8.2)
    # -----------------------------------------------------------
    async def add_fban(self, user_id: int, reason: str, admin_id: int):
        """Add a user to the global ban list."""
        await self.set("fban_list", str(user_id), {"reason": reason, "admin": admin_id, "date": int(time.time())})

    async def remove_fban(self, user_id: int):
        """Remove a user from the global ban list."""
        await self.delete("fban_list", str(user_id))

    async def get_fban(self, user_id: int):
        """Check if user is fbanned. Returns dict or None."""
        return await self.get("fban_list", str(user_id))

