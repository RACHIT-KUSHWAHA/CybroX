import asyncio
import os
import sys

# Add working directory to path
sys.path.append(os.getcwd())

from userbot.database.all_db import LocalDB
from userbot.database.universal import UniversalDBManager

async def test_db():
    print("Testing LocalDB directly...")
    db = LocalDB()
    test_key = "test_unicode_🔥"
    test_val = "value_with_emoji_🚀"
    
    # 1. Test Set
    db.set(test_key, test_val)
    print(f"Set {test_key} = {test_val}")
    
    # 2. Test Get
    got_val = db.get(test_key)
    print(f"Get {test_key} = {got_val}")
    
    assert got_val == test_val, "LocalDB Get failed!"
    print("LocalDB Direct Test Passed!")

    print("\nTesting UniversalDBManager...")
    # Initialize with local mode only
    univ = UniversalDBManager(local_db_name="test_univ.db")
    await univ.init_database()
    
    # 3. Test Universal Set
    await univ.set("test_col", "key1", "val1")
    print("Universal Set completed.")
    
    # 4. Test Universal Get
    val = await univ.get("test_col", "key1")
    print(f"Universal Get: {val}")
    assert val == "val1", "Universal Get failed!"
    
    # 5. Test Universal Get with Default (The fix)
    default_val = await univ.get("test_col", "non_existent", default="default_ret")
    print(f"Universal Get Default: {default_val}")
    assert default_val == "default_ret", "Universal Get Default failed!"
    
    await univ.close()
    print("UniversalDBManager Test Passed!")

if __name__ == "__main__":
    asyncio.run(test_db())
