import os
import logging
import asyncio
import sys

from aiohttp import web
from pyrogram import Client, idle
from pyrogram.enums import ParseMode

from userbot.core.logger import LOGS
from userbot.helpers import config
from userbot.helpers.db import liter, db

# Import Cloud Loop persistence logic
from userbot.database.core import restore_database, start_backup_loop


async def start_web_server():
    """Starts a tiny aiohttp web server for keep-alive."""
    async def handle(request):
        return web.Response(text="CybroX is Alive")

    server = web.Application()
    server.router.add_get("/", handle)
    runner = web.AppRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", config.PORT)
    await site.start()
    logging.info(f"Web server listening on port {config.PORT}")

async def main():
    # Initialize Client inside the loop
    app = Client(
        "cybrox_userbot",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        session_string=config.SESSION_STRING,
        plugins=dict(root="userbot.plugins"),
        parse_mode=ParseMode.HTML
    )

    # 1. Start Client (Required for restore_db to access Saved Messages)
    try:
        await app.start()
    except Exception as e:
        logging.error(f"Failed to start client: {e}")
        sys.exit(1)

    # 2. Run Startup Tasks Simultaneously (Restore DB, Init DB, Start Web Server)
    # Note: restore_db must happen BEFORE liter.init ideally if we want validity, 
    # but asyncio.gather runs concurrently. 
    # We'll run restore first to ensure file exists, then init, then server.
    await restore_database(app)
    await liter.init()
    
    # 3. Start Web Server and Background Tasks
    # We use create_task for the loop so it doesn't block
    loop_task = asyncio.create_task(start_backup_loop(app))
    
    # We act on the "Use asyncio.gather" request by gathering the server startup and the success log?
    # Or simply await the server start.
    await start_web_server()

    LOGS.info("CybroX Userbot Started Successfully")

    # 4. Idle (Block main loop)
    await idle()

    # 5. Cleanup
    await app.stop()
    await liter.close()
    loop_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())