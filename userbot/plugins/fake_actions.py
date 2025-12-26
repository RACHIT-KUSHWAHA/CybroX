from pyrogram import Client, filters, enums
from pyrogram.types import Message
import asyncio
from userbot.helpers.misc import modules_help, prefix
from userbot.helpers.managers import edit_or_reply

@Client.on_message(filters.command("type", prefix) & filters.me)
async def type_cmd(client: Client, message: Message):
    """Fake typing action."""
    await message.delete()
    async with client.action(message.chat.id, enums.ChatAction.TYPING):
        await asyncio.sleep(5) # Type for 5 seconds

@Client.on_message(filters.command("upload", prefix) & filters.me)
async def upload_cmd(client: Client, message: Message):
    """Fake upload action."""
    await message.delete()
    async with client.action(message.chat.id, enums.ChatAction.UPLOAD_DOCUMENT):
        await asyncio.sleep(5)

@Client.on_message(filters.command("game", prefix) & filters.me)
async def game_cmd(client: Client, message: Message):
    """Fake playing game action."""
    await message.delete()
    async with client.action(message.chat.id, enums.ChatAction.PLAYING):
        await asyncio.sleep(5)

@Client.on_message(filters.command("video", prefix) & filters.me)
async def video_cmd(client: Client, message: Message):
    """Fake recording video action."""
    await message.delete()
    async with client.action(message.chat.id, enums.ChatAction.RECORD_VIDEO):
        await asyncio.sleep(5)
        
@Client.on_message(filters.command("voice", prefix) & filters.me)
async def voice_cmd(client: Client, message: Message):
    """Fake recording voice action."""
    await message.delete()
    async with client.action(message.chat.id, enums.ChatAction.RECORD_AUDIO):
        await asyncio.sleep(5)

modules_help["fake_actions"] = {
    "type": "Fake typing status",
    "upload": "Fake uploading document status",
    "game": "Fake playing game status",
    "video": "Fake recording video status",
    "voice": "Fake recording audio status",
    "__category__": "fun"
}
