
import os
import google.generativeai as genai
from dotenv import load_dotenv
from userbot.core.logger import LOGS
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

LOGS.info("--- START MODELS ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            LOGS.info(m.name)
except Exception as e:
    LOGS.error(f"ERROR: {e}")
LOGS.info("--- END MODELS ---")
