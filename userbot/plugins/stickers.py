#  Legendbot-UserBot - telegram userbot
#  Copyright (C) 2025 Legendbot UserBot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

import io
import os
import math
import asyncio
import random
from typing import Optional, Tuple, Union
from PIL import Image

from pyrogram import Client, filters, errors
from pyrogram.types import Message
from pyrogram.raw.functions.messages import GetStickerSet
from pyrogram.raw.types import InputStickerSetShortName

from userbot.helpers.misc import modules_help, prefix
from userbot.helpers.managers import edit_or_reply, with_reply
from userbot.helpers.db import db


async def resize_image(image: bytes, is_sticker: bool = False) -> bytes:
    """Resize image to sticker-friendly size"""
    image = Image.open(io.BytesIO(image))
    
    # Handle RGBA vs RGB
    if image.mode == "RGBA":
        mode = "RGBA"
    else:
        mode = "RGB"
        image = image.convert("RGB")
    
    # Calculate dimensions
    size = 512
    width, height = image.size
    
    # Preserve aspect ratio within Telegram's requirements
    if width > height:
        new_width = size
        new_height = int(height * (size / width))
    else:
        new_height = size
        new_width = int(width * (size / height))
        
    image = image.resize((new_width, new_height))
    
    # Create centered image
    new_image = Image.new(mode, (size, size), (0, 0, 0, 0))
    x_offset = (size - new_width) // 2
    y_offset = (size - new_height) // 2
    new_image.paste(image, (x_offset, y_offset), image if mode == "RGBA" else None)
    
    # Convert to bytes
    output = io.BytesIO()
    if is_sticker:
        new_image.save(output, format="WEBP")
    else:
        new_image.save(output, format="PNG")
    output.seek(0)
    
    return output.getvalue()


@Client.on_message(filters.command(["kang", "k"], prefix) & filters.me)
async def kang_cmd(client: Client, message: Message):
    """OmniKang: Add any sticker/image/video to your pack"""
    msg = await edit_or_reply(message, "<b>🔄 OmniKang Processing...</b>")
    
    # Check for necessary elements (replied message or attachment)
    replied = message.reply_to_message
    if not replied:
        await msg.edit("<b>❌ Reply to a sticker, image, or video!</b>")
        await asyncio.sleep(3)
        await msg.delete()
        return
    
    # Get sticker pack details from user's settings or defaults
    user = await client.get_me()
    pack_prefix = await db.get("stickers", "pack_prefix", "Legendbot_")
    max_stickers = 120
    
    # Determine Media Type
    is_animated = False
    is_video = False
    file_path = None
    emoji = "🤔"
    
    # Check custom emoji in command
    if len(message.command) > 1:
        emoji = message.command[1]
    
    try:
        if replied.sticker:
            file_id = replied.sticker.file_id
            is_animated = replied.sticker.is_animated
            is_video = replied.sticker.is_video
            if not len(message.command) > 1:
                emoji = replied.sticker.emoji or "🤔"
            
            await msg.edit("<b>⬇️ Downloading sticker...</b>")
            file_path = await client.download_media(replied)
            
        elif replied.photo:
            await msg.edit("<b>⬇️ Downloading photo...</b>")
            # Photos need resizing
            file = await client.download_media(replied)
            with open(file, "rb") as f:
                image_data = f.read()
            image_data = await resize_image(image_data, True)
            
            file_path = file + ".webp"
            with open(file_path, "wb") as f:
                f.write(image_data)
            os.remove(file) # Clean orig
            
        elif replied.document:
            mime = replied.document.mime_type or ""
            if "image" in mime:
                # Treat as photo
                await msg.edit("<b>⬇️ Downloading document image...</b>")
                file = await client.download_media(replied)
                with open(file, "rb") as f:
                    image_data = f.read()
                image_data = await resize_image(image_data, True)
                file_path = file + ".webp"
                with open(file_path, "wb") as f:
                    f.write(image_data)
                os.remove(file)
            elif "video" in mime or "webm" in mime:
                # Treat as Video Sticker (simplified expectation: it is already webm/mp4 suitable)
                # Proper video conversion requires ffmpeg, assuming source is compatible for Lite
                is_video = True
                await msg.edit("<b>⬇️ Downloading video...</b>")
                file_path = await client.download_media(replied)
            else:
                await msg.edit("<b>❌ Unsupported file type!</b>")
                return

        elif replied.animation:
            is_video = True
            await msg.edit("<b>⬇️ Downloading animation...</b>")
            file_path = await client.download_media(replied)
            
        else:
            await msg.edit("<b>❌ Media not found!</b>")
            return
            
        # Determine Pack Name based on Type
        if is_animated:
            pack_suffix = "_anim"
            pack_title = f"{user.first_name}'s Anim Pack"
        elif is_video:
            pack_suffix = "_vid"
            pack_title = f"{user.first_name}'s Vid Pack"
        else:
            pack_suffix = ""
            pack_title = f"{user.first_name}'s Pack"
            
        pack_name = f"{pack_prefix}{user.id}{pack_suffix}"
        
        # --- Logic to Create/Append Stickerset ---
        # (This logic repeats searching for available pack slots)
        
        # Try to find or create the sticker pack
        await msg.edit(f"<b>🔍 Selecting pack: {pack_name}...</b>")
        
        # Recursive function to find valid pack number
        found_pack = False
        pack_number = 1
        final_pack_name = pack_name
        final_pack_title = pack_title
        
        while not found_pack:
            if pack_number > 1:
                final_pack_name = f"{pack_name}_{pack_number}"
                final_pack_title = f"{pack_title} {pack_number}"
            
            try:
                sticker_set = await client.invoke(
                    GetStickerSet(
                        stickerset=InputStickerSetShortName(short_name=final_pack_name),
                        hash=0
                    )
                )
                if sticker_set.set.count < max_stickers:
                    found_pack = True # Found existing non-full pack
                else:
                    pack_number += 1 # Pack full, try next
            except errors.StickersetInvalid:
                 found_pack = True # Pack doesn't exist, we will create it
                 sticker_set = None # Flag to create

        # Action: Create or Add
        try:
            if sticker_set is None:
                await msg.edit(f"<b>🆕 Creating new pack: {final_pack_title}...</b>")
                if is_animated:
                    await client.create_animated_sticker_set(
                        user_id=user.id,
                        title=final_pack_title,
                        short_name=final_pack_name,
                        stickers=[{"file": file_path, "emoji": emoji}]
                    )
                elif is_video:
                    await client.create_video_sticker_set(
                        user_id=user.id,
                        title=final_pack_title,
                        short_name=final_pack_name,
                        stickers=[{"file": file_path, "emoji": emoji}]
                    )
                else:
                    await client.create_sticker_set(
                        user_id=user.id,
                        title=final_pack_title,
                        short_name=final_pack_name,
                        stickers=[{"file": file_path, "emoji": emoji}]
                    )
            else:
                await msg.edit(f"<b>➕ Adding to {final_pack_title}...</b>")
                if is_animated:
                    await client.add_animated_sticker_to_set(
                        user_id=user.id,
                        short_name=final_pack_name,
                        sticker={"file": file_path, "emoji": emoji}
                    )
                elif is_video:
                    await client.add_video_sticker_to_set(
                        user_id=user.id,
                        short_name=final_pack_name,
                        sticker={"file": file_path, "emoji": emoji}
                    )
                else:
                    await client.add_sticker_to_set(
                        user_id=user.id,
                        short_name=final_pack_name,
                        sticker={"file": file_path, "emoji": emoji}
                    )
                    
            await msg.edit(
                f"<b>✅ OmniKang Success!</b>\n"
                f"<b>Emoji:</b> {emoji}\n"
                f"<b>Pack:</b> <a href='https://t.me/addstickers/{final_pack_name}'>{final_pack_title}</a>"
            )
            
        except Exception as e:
            await msg.edit(f"<b>❌ Telegram API Error:</b> {e}")
            
    except Exception as e:
        await msg.edit(f"<b>❌ Error processing media:</b> {e}")
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)


@Client.on_message(filters.command("stickerinfo", prefix) & filters.me)
async def sticker_info_cmd(client: Client, message: Message):
    """Get info about a sticker"""
    replied = message.reply_to_message
    
    if not replied or not replied.sticker:
        await edit_or_reply(message, "<b>❌ Reply to a sticker to get info!</b>")
        await asyncio.sleep(3)
        await message.delete()
        return
    
    sticker = replied.sticker
    
    info_text = "<b>🔍 Sticker Information</b>\n\n"
    info_text += f"<b>File ID:</b> <code>{sticker.file_id}</code>\n"
    info_text += f"<b>Emoji:</b> {sticker.emoji}\n"
    info_text += f"<b>Set ID:</b> <code>{sticker.set_id}</code>\n"
    info_text += f"<b>Is Animated:</b> {'✅' if sticker.is_animated else '❌'}\n"
    info_text += f"<b>Is Video:</b> {'✅' if sticker.is_video else '❌'}\n"
    info_text += f"<b>Width:</b> {sticker.width}px\n"
    info_text += f"<b>Height:</b> {sticker.height}px\n"
    info_text += f"<b>File Size:</b> {sticker.file_size / 1024} KB\n"
    
    await edit_or_reply(message, info_text)