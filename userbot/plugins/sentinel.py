# Module: sentinel.py
# Description: Sentinel (Malware Scanner & File Sanitizer)
# Copyright (C) 2025 CybroX UserBot Organization

import os
import hashlib
import aiohttp
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

from userbot.helpers.misc import modules_help, prefix
from userbot.helpers.scripts import edit_or_reply

# You should add VT_API_KEY to your .env file
VT_API_KEY = os.getenv("VT_API_KEY", None)

async def calculate_hash(file_path):
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

@Client.on_message(filters.command(["scan", "vt"], prefix) & filters.me)
async def scan_cmd(client: Client, message: Message):
    """Scan file for malware using VirusTotal logic"""
    msg = await edit_or_reply(message, "<b>🛡️ Sentinel: Analyzing...</b>")
    
    replied = message.reply_to_message
    if not replied or not replied.media:
        await msg.edit("<b>❌ Reply to a file/media to scan it!</b>")
        return
    
    try:
        # 1. Download File
        await msg.edit("<b>⬇️ Downloading for hashing...</b>")
        file = await client.download_media(replied)
        
        # 2. Calculate Hash
        await msg.edit("<b>🧮 Calculating SHA256 Hash...</b>")
        file_hash = await calculate_hash(file)
        
        # Clean up file immediately
        if os.path.exists(file):
            os.remove(file)
        
        # 3. Check VirusTotal
        vt_link = f"https://www.virustotal.com/gui/file/{file_hash}"
        
        if VT_API_KEY:
            await msg.edit(f"<b>🔍 Querying VirusTotal API...</b>\nHash: <code>{file_hash[:10]}...</code>")
            
            async with aiohttp.ClientSession() as session:
                headers = {"x-apikey": VT_API_KEY}
                async with session.get(f"https://www.virustotal.com/api/v3/files/{file_hash}", headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
                        
                        malicious = stats.get("malicious", 0)
                        suspicious = stats.get("suspicious", 0)
                        harmless = stats.get("harmless", 0)
                        
                        color = "🟢"
                        if malicious > 0:
                            color = "🔴"
                        elif suspicious > 0:
                            color = "🟡"
                            
                        report = (
                            f"<b>🛡️ Sentinel Scan Result</b>\n\n"
                            f"<b>Status:</b> {color} <b>{malicious} engines flagged this.</b>\n"
                            f"<b>Suspicious:</b> {suspicious}\n"
                            f"<b>Safe:</b> {harmless}\n\n"
                            f"<b>SHA256:</b> <code>{file_hash}</code>\n"
                            f"🔗 <a href='{vt_link}'>View Full Report</a>"
                        )
                        await msg.edit(report)
                    elif resp.status == 404:
                         await msg.edit(
                            f"<b>⚠️ Unknown File</b>\n\n"
                            f"VirusTotal has not seen this file before.\n"
                            f"<b>SHA256:</b> <code>{file_hash}</code>\n\n"
                            f"🔗 <a href='{vt_link}'>Upload & Analyze Manually</a>"
                        )
                    else:
                        await msg.edit(f"<b>❌ API Error:</b> {resp.status}")
        else:
            # Fallback if no Key
            await msg.edit(
                f"<b>🛡️ Sentinel Hashing Engine</b>\n\n"
                f"<b>SHA256:</b> <code>{file_hash}</code>\n\n"
                f"⚠️ <b>No API Key Configured.</b>\n"
                f"🔗 <a href='{vt_link}'>Click here to check VirusTotal manually</a>"
            )
            
    except Exception as e:
        await msg.edit(f"<b>❌ Sentinel Error:</b> {str(e)}")
        # Verify cleanup
        if 'file' in locals() and os.path.exists(file):
            os.remove(file)

modules_help["sentinel"] = {
    "scan [reply]": "Calculate hash & check VirusTotal",
    "vt [reply]": "Alias for scan",
    "__category__": "security"
}
