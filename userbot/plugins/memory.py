from pyrogram import Client, filters
from pyrogram.types import Message
from userbot.helpers.managers import edit_or_reply
from userbot.helpers.db import liter
from userbot.helpers.misc import prefix
import time

# --- Watcher: Global Message Listener ---
# We listen to ALL messages (incoming & outgoing) to index them.
# Group=-1 ensures this runs alongside other handlers without stopping propagation.

@Client.on_message(group=-1)
async def memory_watcher(client: Client, message: Message):
    # Only index text messages
    if not message.text:
        return
    
    # Skip service messages or empty ones
    if not message.chat:
        return

    # Prepare data
    mid = message.id
    cid = message.chat.id
    text = message.text
    # Safely get timestamp
    ts = message.date.timestamp() if message.date else time.time()
    # Safely get sender ID
    sid = message.from_user.id if message.from_user else 0

    # Index into FTS5
    # This is "fire and forget" - we don't await the result to block the loop heavily,
    # but we do await the DB call itself which is async.
    try:
        await liter.insert_message_index(mid, cid, text, ts, sid)
    except Exception as e:
        # Silently fail logging in watcher to avoid log spam
        pass


@Client.on_message(filters.command(["recall", "remember"], prefix) & filters.me)
async def recall_cmd(client: Client, message: Message):
    """
    Search your chat memory.
    Usage: .recall [query]
    """
    cmd = message.command
    if len(cmd) < 2:
        await edit_or_reply(message, "<b>🧠 Memory:</b> Please provide a search query.\nExample: <code>.recall api key</code>")
        return

    query = " ".join(cmd[1:])
    msg = await edit_or_reply(message, f"<b>🧠 Searching memory for:</b> <code>{query}</code>...")

    # Perform FTS5 Search
    try:
        results = await liter.search_messages(query, limit=10)
    except Exception as e:
        await msg.edit(f"<b>❌ Memory Error:</b> {str(e)}")
        return

    if not results:
        await msg.edit(f"<b>🧠 Memory:</b> No matches found for <code>{query}</code>.")
        return

    # Format Results
    out = f"<b>🧠 Memory Recall ({len(results)} matches):</b>\n\n"
    
    for res in results:
        # Create a link if it's a supergroup/channel
        chat_id = res['chat_id']
        msg_id = res['message_id']
        text = res['text'][:100].replace("<", "&lt;").replace(">", "&gt;") # Truncate and escape
        
        # timestamp to readable
        ts_str = time.strftime('%Y-%m-%d', time.localtime(res['timestamp']))

        # Attempt to link (only works for public/private supergroups, not basic groups)
        # We can format a rough link
        if str(chat_id).startswith("-100"):
            link = f"https://t.me/c/{str(chat_id)[4:]}/{msg_id}"
            out += f"• <a href='{link}'>[{ts_str}]</a>: {text}\n"
        else:
            out += f"• [{ts_str}] (Chat {chat_id}): {text}\n"

    await msg.edit(out, disable_web_page_preview=True)


@Client.on_message(filters.command("wipe_memory", prefix) & filters.me)
async def wipe_memory_cmd(client: Client, message: Message):
    """
    Wipe the entire FTS5 index.
    Usage: .wipe_memory
    """
    msg = await edit_or_reply(message, "<b>⚠️ Wiping Memory Index...</b>")
    try:
        await liter.wipe_fts_index()
        await msg.edit("<b>🧠 Memory Wiped:</b> I have forgotten everything.")
    except Exception as e:
        await msg.edit(f"<b>❌ Error:</b> {str(e)}")
