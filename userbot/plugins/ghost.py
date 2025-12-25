
from pyrogram import Client, filters
from pyrogram.types import Message
from userbot.helpers.misc import modules_help, prefix
from userbot.helpers.scripts import edit_or_reply

# Global state for Ghost Mode
GHOST_MODE = False

@Client.on_message(filters.command("ghost", prefix) & filters.me)
async def ghost_cmd(client: Client, message: Message):
    """
    Toggle Ghost Mode.
    Usage: .ghost on/off
    """
    global GHOST_MODE
    
    if len(message.command) < 2:
        status = "ON" if GHOST_MODE else "OFF"
        await edit_or_reply(message, f"<b>👻 Ghost Mode is currently: {status}</b>")
        return

    arg = message.command[1].lower()
    
    if arg == "on":
        GHOST_MODE = True
        await edit_or_reply(message, "<b>👻 Ghost Mode Enabled. Passing messages to Saved Messages silently.</b>")
    elif arg == "off":
        GHOST_MODE = False
        await edit_or_reply(message, "<b>👻 Ghost Mode Disabled.</b>")
    else:
        await edit_or_reply(message, "<b>❌ Usage: </b><code>.ghost on/off</code>")


# Watcher for incoming messages when Ghost Mode is ON
# We filter for private messages that are NOT from me, and not from a bot (optional)
# We use a high group number to ensure this runs
@Client.on_message(filters.private & ~filters.me, group=1)
async def ghost_watcher(client: Client, message: Message):
    if GHOST_MODE:
        sender = message.from_user
        name = sender.first_name if sender else "Unknown"
        
        # Forward to Saved Messages
        # We construct a summary so we don't trigger "forwarded from" if we don't want to, 
        # but forwarding is easiest to see the content.
        # However, to avoid 'Seen' we just act as a passive observer. 
        # Pyrogram doesn't mark read unless we do specific actions.
        # But we want to see the message in Saved Messages so we don't HAVE to open the chat.
        
        try:
            # Send a summary to Saved Messages
            text_preview = message.text or "[Media/Service Message]"
            
            log_text = f"<b>👻 Ghost Alert</b>\n" \
                       f"<b>From:</b> {name} (`{sender.id if sender else 'Control'}`)\n" \
                       f"<b>Chat:</b> {message.chat.id}\n\n" \
                       f"{text_preview}"
            
            await client.send_message("me", log_text)
            
            # If it has media/file, maybe forward it without quoting?
            # message.forward("me") might be better but it shows "Forwarded from X".
            # If user has privacy on forwards, it might be hidden. 
            # Simple Text summary is safer for stealth reading.
        except Exception as e:
            pass

modules_help["ghost"] = {
    "ghost on/off": "Toggle Ghost Mode. When ON, incoming PMs are forwarded to Saved Messages.",
}
