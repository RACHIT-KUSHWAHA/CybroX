from pyrogram import Client, filters
from pyrogram.types import Message
from userbot.helpers.misc import modules_help, prefix
from userbot.helpers.managers import edit_or_reply
import aiohttp
import io

@Client.on_message(filters.command("carbon", prefix) & filters.me)
async def carbon_cmd(client: Client, message: Message):
    """
    Make your code look beautiful with Carbon!
    Usage: .carbon [code] or reply to code.
    """
    if len(message.command) > 1:
        code = message.text.split(maxsplit=1)[1]
    elif message.reply_to_message:
        code = message.reply_to_message.text or message.reply_to_message.caption
    else:
        await edit_or_reply(message, "<b>Provide some code to carbonize!</b>")
        return

    if not code:
        await edit_or_reply(message, "<b>Give me text, not silence!</b>")
        return

    msg = await edit_or_reply(message, "<b>🎨 Painting your code...</b>")

    try:
        url = "https://carbonara.solopov.dev/api/cook"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={"code": code}) as resp:
                if resp.status != 200:
                    await msg.edit("<b>Carbon API Failed!</b>")
                    return
                image = io.BytesIO(await resp.read())
                image.name = "carbon.png"
        
        await client.send_photo(
            message.chat.id,
            image,
            caption=f"<b>Carbonized by LegendBot</b> ⚡",
            reply_to_message_id=message.reply_to_message_id or message.id
        )
        await msg.delete()
    except Exception as e:
        await msg.edit(f"<b>Error:</b> {str(e)}")

modules_help["carbon"] = {
    "carbon [code/reply]": "Create a beautiful snippet of your code",
    "__category__": "utils"
}
