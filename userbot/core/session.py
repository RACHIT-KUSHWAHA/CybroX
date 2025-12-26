from pyrogram import Client
from pyrogram.enums import ParseMode
from userbot.helpers import config


app = Client(
    "cybrox_userbot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    session_string=config.SESSION_STRING,
    plugins=dict(root="userbot.plugins"),
    parse_mode=ParseMode.HTML
)


