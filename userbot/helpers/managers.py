import asyncio
import os
from pyrogram.enums import ParseMode
from pyrogram.types import Message, LinkPreviewOptions
from userbot.helpers.utils.format import md_to_text, paste_message
from userbot.database.sudouser_db import sudousers_list

# Rebrand: Helper Manager for Legendbot

async def edit_or_reply(
    message: Message,
    text: str,
    parse_mode=ParseMode.HTML,
    link_preview=False,
    file_name=None,
    aslink=False,
    deflink=False,
    noformat=False,
    linktext=None,
    caption=None,
):
    """
    Intelligent message handler:
    - Edits the message if sent by the user (self).
    - Replies if sent by a Sudo User (or others if configured).
    - Handles pagination/pastebin for large texts.
    """
    sudo_users = sudousers_list()
    reply_to = message.reply_to_message

    # 1. Size Check & Pastebin Fallback
    if len(text) < 4096 and not deflink:
        if message.from_user and message.from_user.id in sudo_users:
            if reply_to:
                return await reply_to.reply_text(
                    text,
                    parse_mode=parse_mode,
                    link_preview_options=LinkPreviewOptions(),
                )
            return await message.reply_text(
                text,
                parse_mode=parse_mode,
                link_preview_options=LinkPreviewOptions(),
            )

        # Self-Edit
        try:
            await message.edit_text(
                text,
                parse_mode=parse_mode,
                link_preview_options=LinkPreviewOptions(),
            )
        except Exception:
            # Fallback if edit fails (e.g., message too old or type mismatch) - Rare but possible
            return await message.reply_text(text, parse_mode=parse_mode, link_preview_options=LinkPreviewOptions())
        
        return message

    # 2. Large Text Handling (Bin)
    if not noformat:
        text = md_to_text(text)

    if aslink or deflink:
        linktext = linktext or "Message was too big, pasted to bin:"
        response = await paste_message(text, pastetype="s")
        text = f"{linktext} <a href='{response}'>here</a>"

        if message.from_user and message.from_user.id in sudo_users:
            if reply_to:
                return await reply_to.reply_text(text, link_preview_options=LinkPreviewOptions())
            return await message.reply_text(text, link_preview_options=LinkPreviewOptions())

        await message.edit_text(text, link_preview_options=LinkPreviewOptions())
        return message

    # 3. File Fallback
    file_name = file_name or "output.txt"
    with open(file_name, "w+", encoding="utf-8") as output:
        output.write(text)

    if reply_to:
        await reply_to.reply_document(file_name, caption=caption)
        await message.delete()
        os.remove(file_name)
        return

    if message.from_user and message.from_user.id in sudo_users:
        await message.reply_document(file_name, caption=caption)
        await message.delete()
        os.remove(file_name)
        return

    await message.reply_document(file_name, caption=caption)
    await message.delete()
    os.remove(file_name)


async def edit_delete(
    message: Message,
    text: str,
    time: int = 10,
    parse_mode=ParseMode.HTML,
    link_preview=False,
):
    """
    Edits a message and then deletes it after `time` seconds.
    Useful for status updates like 'Processing...'
    """
    sudo_users = sudousers_list()
    sent = None

    if message.from_user and message.from_user.id in sudo_users:
        reply_to = message.reply_to_message
        if reply_to:
            sent = await reply_to.reply_text(
                text,
                parse_mode=parse_mode,
                link_preview_options=LinkPreviewOptions(),
            )
        else:
            sent = await message.reply_text(
                text,
                parse_mode=parse_mode,
                link_preview_options=LinkPreviewOptions(),
            )
    else:
        try:
            sent = await message.edit_text(
                text,
                parse_mode=parse_mode,
                link_preview_options=LinkPreviewOptions(),
            )
        except Exception:
             sent = await message.reply_text(text, parse_mode=parse_mode)

    await asyncio.sleep(time)
    if sent:
        try:
            await sent.delete()

        except:
            pass

import sys
import os

# Backward Compatibility
with_reply = edit_or_reply

def restart():
    os.execl(sys.executable, sys.executable, "main.py")



