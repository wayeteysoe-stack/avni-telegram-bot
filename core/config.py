# core/config.py
import os
import dotenv

# Load environment variables
dotenv.load_dotenv()

# ==========================
# Telegram Config
# ==========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# ==========================
# Gemini AI Config
# ==========================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# New SDK strict production string identifier
MODEL_NAME = "gemini-3.5-flash"

# ==========================
# Memory & Token Pipeline Optimization
# ==========================
# Free Tier quota management ke liye history limit ko balanced (10) rakha hai
HISTORY_LIMIT = 10

# ==========================
# Network Retry Architecture
# ==========================
MAX_RETRIES = 3
RETRY_DELAY = 2
REQUEST_TIMEOUT = 25

# ==========================
# Server Configuration
# ==========================
PORT = int(os.getenv("PORT", 10000))

# ==========================
# Debug Mode
# ==========================
DEBUG = False
