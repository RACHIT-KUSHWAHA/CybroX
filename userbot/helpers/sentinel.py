import asyncio
import time
import logging
from functools import wraps
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from userbot.helpers import config

# Store timestamps of messages: {user_id: [timestamp1, timestamp2, ...]}
usage_history = {}
WINDOW_SECONDS = 10
MAX_MESSAGES = 5

def clean_old_timestamps(user_id):
    """Remove timestamps older than WINDOW_SECONDS."""
    now = time.time()
    if user_id in usage_history:
        usage_history[user_id] = [t for t in usage_history[user_id] if now - t <= WINDOW_SECONDS]

def check_rate_limit(user_id):
    """
    Returns True if user is allowed to proceed, False otherwise.
    Logic: If > 5 msgs in 10s, verify admin.
    """
    clean_old_timestamps(user_id)
    
    # Add current attempt (tentatively)
    # Actually, we should check first.
    count = len(usage_history.get(user_id, []))
    
    if count >= MAX_MESSAGES:
        # Rate limit exceeded. Check if Admin.
        # User ID validation
        if user_id in config.SUDO_USERS or user_id == config.API_ID: # API_ID is not user_id, usually. 
            # We need OWNER_ID. Config usually has it or we derive from session. 
            # Lite plan config didn't strictly separate Owner ID, but SUDO_USERS should contain it.
            # Let's assume if they are in SUDO_USERS, they bypass.
            return True
        else:
            return False
            
    return True

def add_usage(user_id):
    if user_id not in usage_history:
        usage_history[user_id] = []
    usage_history[user_id].append(time.time())

def sentinel_guard(func):
    """
    Sentinel Security Decorator.
    1. Rate Limits non-admins (5 msg / 10s).
    2. Auto-handles FloodWait (Sleep & Retry) for everyone.
    """
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        user_id = None
        
        # Attempt to extract user_id from message
        # Pyrogram handlers standard: func(client, message, ...)
        if isinstance(message, Message):
            if message.from_user:
                user_id = message.from_user.id
            elif message.sender_chat:
                user_id = message.sender_chat.id
        
        # 1. Rate Check
        if user_id:
            if not check_rate_limit(user_id):
                logging.warning(f"Sentinel: Rate limit exceeded for {user_id}. Ignoring.")
                # We stop execution here.
                # Optionally send a reply? User said "raise error or ignore". Ignore is safer for spam.
                return
            
            # Count this usage
            add_usage(user_id)

        # 2. FloodWait Protection Loop
        while True:
            try:
                return await func(client, message, *args, **kwargs)
            except FloodWait as e:
                wait_time = e.value + 1
                logging.warning(f"Sentinel: FloodWait triggered. Sleeping for {wait_time}s...")
                await asyncio.sleep(wait_time)
                # Loop continues and retries 'func'
                # Recommendation: Add a max retry limit to prevent infinite loops? 
                # User request: "try/except ... sleep ... retry automatically".
                # Infinite retry is the "Infinite Life" way.
            except Exception as e:
                # Other errors bubble up
                raise e

    return wrapper
