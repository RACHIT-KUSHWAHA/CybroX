import asyncio
import os

from pyrogram.enums import ParseMode

from ..helpers.utils.format import md_to_text, paste_message
from database.sudouser_db import is_sudouser, sudousers_list


async def edit_or_reply(
    message,
    text,
    parse_mode=None,
    link_preview=False,
    file_name=None,
    aslink=False,
    deflink=False,
    noformat=False,
    linktext=None,
    caption=None,
):
    sudo_users = sudousers_list()
    parse_mode = parse_mode or ParseMode.MARKDOWN

    reply_to = message.reply_to_message

    # Normal edit / reply
    if len(text) < 4096 and not deflink:
        if message.from_user and message.from_user.id in sudo_users:
            if reply_to:
                return await reply_to.reply_text(
                    text,
                    parse_mode=parse_mode,
                    disable_web_page_preview=not link_preview,
                )
            return await message.reply_text(
                text,
                parse_mode=parse_mode,
                disable_web_page_preview=not link_preview,
            )

        await message.edit_text(
            text,
            parse_mode=parse_mode,
            disable_web_page_preview=not link_preview,
        )
        return message

    # Convert markdown to plain text if needed
    if not noformat:
        text = md_to_text(text)

    # Paste as link
    if aslink or deflink:
        linktext = linktext or "Message was too big so pasted to bin"
        response = await paste_message(text, pastetype="s")
        text = f"{linktext} [here]({response})"

        if message.from_user and message.from_user.id in sudo_users:
            if reply_to:
                return await reply_to.reply_text(
                    text,
                    disable_web_page_preview=not link_preview,
                )
            return await message.reply_text(
                text,
                disable_web_page_preview=not link_preview,
            )

        await message.edit_text(
            text,
            disable_web_page_preview=not link_preview,
        )
        return message

    # Send as file
    file_name = file_name or "output.txt"

    with open(file_name, "w+", encoding="utf-8") as output:
        output.write(text)

    if reply_to:
        await reply_to.reply_document(
            file_name,
            caption=caption,
        )
        await message.delete()
        os.remove(file_name)
        return

    if message.from_user and message.from_user.id in sudo_users:
        await message.reply_document(
            file_name,
            caption=caption,
        )
        await message.delete()
        os.remove(file_name)
        return

    await message._client.send_document(
        message.chat.id,
        file_name,
        caption=caption,
    )
    await message.delete()
    os.remove(file_name)


async def edit_delete(
    message,
    text,
    time=10,
    parse_mode=None,
    link_preview=False,
):
    sudo_users = sudousers_list()
    parse_mode = parse_mode or ParseMode.MARKDOWN

    if message.from_user and message.from_user.id in sudo_users:
        reply_to = message.reply_to_message
        if reply_to:
            sent = await reply_to.reply_text(
                text,
                parse_mode=parse_mode,
                disable_web_page_preview=not link_preview,
            )
        else:
            sent = await message.reply_text(
                text,
                parse_mode=parse_mode,
                disable_web_page_preview=not link_preview,
            )
    else:
        sent = await message.edit_text(
            text,
            parse_mode=parse_mode,
            disable_web_page_preview=not link_preview,
        )

    await asyncio.sleep(time)
    await sent.delete()
