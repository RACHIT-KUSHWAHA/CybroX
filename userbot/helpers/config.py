import os
import logging
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    """
    Configuration holder for Legendbot.
    """
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH", "")
    SESSION_STRING = os.getenv("SESSION_STRING", "") or os.getenv("STRINGSESSION", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", None)
    OWNER_ID = int(os.getenv("OWNER_ID", 0))
    
    # AI Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # Database
    MONGO_URI = os.getenv("MONGO_URI", "")
    REDIS_URL = os.getenv("REDIS_URL", "")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "legendbot.db")
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    
    # Redis Variants (for compatibility)
    REDIS_URI = os.getenv("REDIS_URI", "") or REDIS_URL
    REDISHOST = os.getenv("REDISHOST", "")
    REDISPASSWORD = os.getenv("REDISPASSWORD", "") or REDIS_PASSWORD
    REDISPORT = os.getenv("REDISPORT", "")
    
    # System
    PORT = int(os.getenv("PORT", 8080))
    
    # Sudo
    _sudo_users_str = os.getenv("SUDO_USERS", "")
    SUDO_USERS = {int(x.strip()) for x in _sudo_users_str.split(",") if x.strip().isdigit()}

    # Aesthetics
    ALIVE_PIC = os.getenv("ALIVE_PIC", "https://telegra.ph/file/a7585093557cfc7075253.jpg")
    ALIVE_MSG = os.getenv("ALIVE_MSG", "Legendbot is Alive and Running!")

# Backwards Compatibility (Global Variables)
API_ID = Config.API_ID
API_HASH = Config.API_HASH
SESSION_STRING = Config.SESSION_STRING
BOT_TOKEN = Config.BOT_TOKEN
DB_NAME = Config.DB_NAME
PORT = Config.PORT
SUDO_USERS = Config.SUDO_USERS
OPENAI_API_KEY = Config.OPENAI_API_KEY
GEMINI_API_KEY = Config.GEMINI_API_KEY
DATABASE_URL = Config.DATABASE_URL
REDIS_URI = Config.REDIS_URI
REDISHOST = Config.REDISHOST
REDISPASSWORD = Config.REDISPASSWORD
REDISPORT = Config.REDISPORT
MONGO_URI = Config.MONGO_URI
REDIS_PASSWORD = Config.REDIS_PASSWORD
REDIS_URL = Config.REDIS_URL

# Logging Configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("legendbot.log"), logging.StreamHandler()],
    level=logging.INFO,
)

logging.info(f"Config Loaded. Sudo Users: {len(SUDO_USERS)}")