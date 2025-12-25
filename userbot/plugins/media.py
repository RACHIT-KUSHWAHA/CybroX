import os
import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from userbot.helpers.scripts import edit_or_reply
from userbot.helpers.misc import prefix

# ---------------------------------------------------------------------------------
# Media Module: Song & Video Downloader
# Uses yt-dlp (must be installed via pip)
# ---------------------------------------------------------------------------------

async def download_media(url: str, is_audio: bool = False):
    """
    Downloads media using yt-dlp via subprocess.
    Returns: (title, file_path) or (None, error_message)
    """
    # Create temporary filename
    timestamp = int(time.time())
    out_tmpl = f"downloads/{timestamp}_%(title)s.%(ext)s"
    
    # Base command
    cmd = [
        "yt-dlp",
        "--no-warnings",
        "--format", "bestaudio/best" if is_audio else "bestvideo+bestaudio/best",
        "-o", out_tmpl,
        url
    ]

    if is_audio:
        cmd.extend(["--extract-audio", "--audio-format", "mp3"])

    # Run subproces
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        return None, stderr.decode().strip()

    # Find the downloaded file
    # We look for files starting with the timestamp in the downloads folder
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
        
    for fname in os.listdir("downloads"):
        if fname.startswith(str(timestamp)):
            return fname, os.path.join("downloads", fname)
            
    return None, "File not found after download."


@Client.on_message(filters.command("song", prefix) & filters.me)
async def song_cmd(client: Client, message: Message):
    """
    Download music from YouTube/Spotify.
    Usage: .song [query or link]
    """
    cmd = message.command
    if len(cmd) < 2:
        await edit_or_reply(message, "<b>🎵 Usage:</b> <code>.song [query/link]</code>")
        return

    query = " ".join(cmd[1:])
    msg = await edit_or_reply(message, f"<b>🔎 Searching:</b> <code>{query}</code>")

    # If it's not a link, use "ytsearch:"
    if not query.startswith("http"):
        query = f"ytsearch:{query}"

    await msg.edit("<b>⬇️ Downloading Audio...</b>")
    
    title, path = await download_media(query, is_audio=True)
    
    if not title:
        await msg.edit(f"<b>❌ Download Failed:</b> {path}") # path contains error msg here
        return
        
    await msg.edit("<b>⬆️ Uploading...</b>")
    
    try:
        await client.send_audio(
            chat_id=message.chat.id,
            audio=path,
            title=title.replace(f"{int(time.time())}_", "").replace(".mp3", ""),
            performer="CybroX",
            caption=f"🎵 <b>{title}</b>\nDownloaded by CybroX"
        )
        await msg.delete()
    except Exception as e:
        await msg.edit(f"<b>❌ Upload Failed:</b> {str(e)}")
    finally:
        if os.path.exists(path):
            os.remove(path)


@Client.on_message(filters.command("video", prefix) & filters.me)
async def video_cmd(client: Client, message: Message):
    """
    Download video from YouTube.
    Usage: .video [query or link]
    """
    cmd = message.command
    if len(cmd) < 2:
        await edit_or_reply(message, "<b>🎬 Usage:</b> <code>.video [query/link]</code>")
        return

    query = " ".join(cmd[1:])
    msg = await edit_or_reply(message, f"<b>🔎 Searching:</b> <code>{query}</code>")

    if not query.startswith("http"):
        query = f"ytsearch:{query}"

    await msg.edit("<b>⬇️ Downloading Video...</b>")
    
    title, path = await download_media(query, is_audio=False)
    
    if not title:
        await msg.edit(f"<b>❌ Download Failed:</b> {path}")
        return
        
    await msg.edit("<b>⬆️ Uploading...</b>")
    
    try:
        await client.send_video(
            chat_id=message.chat.id,
            video=path,
            caption=f"🎬 <b>{title}</b>\nDownloaded by CybroX"
        )
        await msg.delete()
    except Exception as e:
        await msg.edit(f"<b>❌ Upload Failed:</b> {str(e)}")
    finally:
        if os.path.exists(path):
            os.remove(path)
