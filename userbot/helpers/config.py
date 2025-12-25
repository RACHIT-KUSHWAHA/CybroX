import os
import logging
from dotenv import load_dotenv

# Load .env file if it exists (for local development)
load_dotenv()

# Essential Configuration
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
SESSION_STRING = os.getenv("SESSION_STRING", "") or os.getenv("STRINGSESSION", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


# Owner and Sudo Users
# Expects a comma-separated list of user IDs in the environment variable
# e.g., SUDO_USERS="12345678, 87654321"
_sudo_users_str = os.getenv("SUDO_USERS", "")
SUDO_USERS = {int(x.strip()) for x in _sudo_users_str.split(",") if x.strip().isdigit()}

# Database Configuration (Lite Plan)
DB_NAME = os.getenv("DB_NAME", "cybrox.db")

# Platform Port (for dummy web server)
PORT = int(os.getenv("PORT", 8080))

# Logging Configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("cybrox.log"), logging.StreamHandler()],
    level=logging.INFO,
)

logging.info(f"Config Loaded. Sudo Users: {len(SUDO_USERS)}")