import os
import google.generativeai as genai
from pyrogram import Client, filters
from pyrogram.types import Message
from userbot.helpers.scripts import edit_or_reply
from userbot.helpers.misc import prefix
from userbot.helpers import config
from userbot.database.core import CybroDB

# Configure Gemini
# Explicitly look for key in env variable first, then config
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    model = None

# We need access to the database singleton to recall memories for context
# But importing 'liter' from utils.db might cause circular imports if not careful.
# Ideally, we just import it.
from userbot.helpers.db import liter


@Client.on_message(filters.command("ask", prefix) & filters.me)
async def ask_cmd(client: Client, message: Message):
    """
    Ask Gemini AI a question.
    Usage: .ask [prompt]
    """
    if not model:
        await edit_or_reply(message, "<b>❌ GEMINI_API_KEY not found in .env!</b>")
        return

    cmd = message.command
    if len(cmd) < 2:
        await edit_or_reply(message, "<b>🤖 Usage:</b> <code>.ask [prompt]</code>")
        return

    prompt = " ".join(cmd[1:])
    msg = await edit_or_reply(message, f"<b>🤖 Thinking:</b> <code>{prompt}</code>")

    try:
        response = await model.generate_content_async(prompt)
        text = response.text
        
        # Markdown formatting
        await msg.edit(f"<b>🤖 Gemini:</b>\n\n{text}")
    except Exception as e:
        await msg.edit(f"<b>❌ AI Error:</b> {str(e)}")


@Client.on_message(filters.command("chat", prefix) & filters.me)
async def chat_cmd(client: Client, message: Message):
    """
    Context-aware Chat with Gemini (RAG Lite).
    Uses last 10 messages from Memory as context.
    Usage: .chat [prompt]
    """
    if not model:
        await edit_or_reply(message, "<b>❌ GEMINI_API_KEY not found in .env!</b>")
        return

    cmd = message.command
    if len(cmd) < 2:
        await edit_or_reply(message, "<b>🧠 Usage:</b> <code>.chat [prompt]</code>")
        return

    prompt = " ".join(cmd[1:])
    msg = await edit_or_reply(message, f"<b>🧠 Recalling Context & Thinking...</b>")

    try:
        # RAG Step 1: Fetch recent context from FTS (or just recent logs if FTS is for search)
        # Actually, let's just search the prompt in memory to find RELEVANT context.
        # This is true RAG.
        context_results = await liter.search_messages(prompt, limit=5)
        
        context_text = ""
        if context_results:
            context_text = "\n".join([f"- {r['text']}" for r in context_results])
        
        # Construct prompt
        full_prompt = (
            f"You are CybroX, a supreme AI assistant. "
            f"Here is some relevant context from my chat history:\n"
            f"{context_text}\n\n"
            f"User Question: {prompt}\n"
            f"Answer concisely."
        )

        response = await model.generate_content_async(full_prompt)
        text = response.text
        
        await msg.edit(f"<b>🧠 Gemini (RAG):</b>\n\n{text}")
    except Exception as e:
        await msg.edit(f"<b>❌ AI Error:</b> {str(e)}")
