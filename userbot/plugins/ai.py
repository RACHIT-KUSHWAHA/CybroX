
import google.generativeai as genai
from openai import AsyncOpenAI
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import g4f

from userbot.core.logger import LOGS
from userbot.helpers import config
from userbot.helpers.misc import modules_help, prefix
from userbot.helpers.scripts import edit_or_reply

# Configure g4f
g4f.debug.logging = False

# Initialize Clients
openai_client = None
gemini_available = False
gemini_model = None

# OpenAI Init
if config.OPENAI_API_KEY:
    try:
        openai_client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
    except Exception as e:
        LOGS.error(f"Failed to init OpenAI: {e}")

# Gemini Configuration
gemini_available = False
if config.GEMINI_API_KEY:
    try:
        genai.configure(api_key=config.GEMINI_API_KEY)
        gemini_available = True
    except Exception as e:
        LOGS.error(f"Failed to init Gemini: {e}")

async def ask_g4f(query):
    """Fallback to g4f if official API fails"""
    try:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.gpt_4o,
            provider=g4f.Provider.DuckDuckGo,
            messages=[{"role": "user", "content": query}],
        )
        return str(response)
    except Exception as e:
        return f"❌ g4f Error: {e}"

@Client.on_message(filters.command(["gpt", "code"], prefix) & filters.me)
async def openai_cmd(client: Client, message: Message):
    """
    Ask OpenAI (Official -> Fallback to g4f).
    Usage: .gpt <query> or .code <query>
    """
    if len(message.command) < 2:
        await edit_or_reply(message, "<b>❌ Usage:</b> <code>.gpt hello</code>")
        return

    query = message.text.split(maxsplit=1)[1]
    msg = await edit_or_reply(message, "<b>🧠 AI Thinking...</b>")
    response = ""
    used_provider = "OpenAI"

    # Try Official OpenAI First
    if openai_client:
        try:
            chat_completion = await openai_client.chat.completions.create(
                messages=[{"role": "user", "content": query}],
                model="gpt-3.5-turbo",
            )
            response = chat_completion.choices[0].message.content
        except Exception as e:
            LOGS.error(f"OpenAI Failed: {e}")
            used_provider = "g4f (Fallback)"
            response = await ask_g4f(query)
    else:
        # No key, go straight to g4f
        used_provider = "g4f (Free)"
        response = await ask_g4f(query)

    # Format output
    if message.command[0] == "code" and "```" not in response:
        response = f"```\n{response}\n```"

    header = f"<b>✨ AI ({used_provider}):</b>\n"
    await send_large_output(client, message, msg, header + response)

async def get_valid_gemini_model():
    """Dynamically find a working model"""
    try:
        # Run list_models in thread as it might block
        models = await asyncio.to_thread(lambda: list(genai.list_models()))
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name or 'pro' in m.name:
                    return m.name
        # Fallback to first available
        if models:
            return models[0].name
    except Exception as e:
        LOGS.error(f"Error listing models: {e}")
    return "models/gemini-pro"

@Client.on_message(filters.command(["gemini", "gem"], prefix) & filters.me)
async def gemini_cmd(client: Client, message: Message):
    """
    Ask Gemini (Auto-Model).
    Usage: .gemini <query>
    """
    if not gemini_available:
        await edit_or_reply(message, "<b>❌ Gemini Config Error.</b> Check logs/key.")
        return

    if len(message.command) < 2:
        await edit_or_reply(message, "<b>❌ Usage:</b> <code>.gemini hello</code>")
        return

    query = message.text.split(maxsplit=1)[1]
    msg = await edit_or_reply(message, "<b>✨ Gemini Thinking...</b>")

    try:
        # Find model dynamically
        model_name = await get_valid_gemini_model()
        
        # Run generation
        response = await client.loop.run_in_executor(None, generate_gemini_content, model_name, query)
        await send_large_output(client, message, msg, f"<b>♊ Gemini ({model_name}):</b>\n{response}")
    except Exception as e:
        await msg.edit(f"<b>❌ Gemini Error:</b> {str(e)}")

def generate_gemini_content(model_name, query):
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(query)
    return response.text

async def send_large_output(client, message, msg, text):
    if len(text) > 4096:
        await msg.delete()
        # Split logic could be better but keeping simple
        await client.send_message(message.chat.id, text[:4096])
        if len(text) > 4096:
             await client.send_message(message.chat.id, text[4096:])
    else:
        await msg.edit(text)

modules_help["ai"] = {
    "gpt <query>": "Ask AI (OpenAI + Free Fallback)",
    "code <query>": "Generate Code",
    "gemini <query>": "Ask Google Gemini",
}
