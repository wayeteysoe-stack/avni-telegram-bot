import os

import dotenv

dotenv.load_dotenv()

import os

# ==========================
# Telegram
# ==========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# ==========================
# Gemini
# ==========================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Purane model 'gemini-2.5-flash' ko hata kar latest standard model set karein
MODEL_NAME = "gemini-2.0-flash"

# ==========================
# Memory
# ==========================
HISTORY_LIMIT = 30

# ==========================
# Retry
# ==========================
MAX_RETRIES = 3
RETRY_DELAY = 2
REQUEST_TIMEOUT = 25

# ==========================
# Server
# ==========================
PORT = int(os.getenv("PORT", 10000))

# ==========================
# Debug
# ==========================
DEBUG = False