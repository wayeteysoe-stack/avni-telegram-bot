import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Token Read
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", os.getenv("TELEGRAM_BOT_TOKEN", ""))

# Conversation Memory Limit
HISTORY_LIMIT = int(os.getenv("HISTORY_LIMIT", 20))

# Fixed & Working Model Name
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-flash-latest")