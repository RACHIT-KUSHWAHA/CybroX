import logging
import asyncio
import sys
from pyrogram import idle
from userbot.core.session import app
from userbot.helpers import config
from userbot.database.core import start_backup_loop

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("legendbot.log"), logging.StreamHandler()],
    level=logging.INFO,
)

async def main():
    # 1. Start Legendbot (Client + DB + Assistant)
    try:
        await app.start()
    except Exception as e:
        logging.error(f"Failed to start Legendbot: {e}")
        sys.exit(1)

    # 2. Start Background Tasks (Backup Loop)
    loop_task = asyncio.create_task(start_backup_loop(app))
    
    logging.info("Legendbot Started Successfully")
    
    # 3. Idle
    await idle()

    # 4. Cleanup
    await app.stop()
    loop_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
