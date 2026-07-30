import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Token Read (Fallback to TELEGRAM_BOT_TOKEN if TELEGRAM_TOKEN not found)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", os.getenv("TELEGRAM_BOT_TOKEN", ""))

# System automatically scans all environment variables starting with 'GEMINI_API_KEY'
GEMINI_API_KEYS = []

for key, value in os.environ.items():
    if key.startswith("GEMINI_API_KEY") and value and value.strip():
        if value.strip() not in GEMINI_API_KEYS:
            GEMINI_API_KEYS.append(value.strip())

MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")

SYSTEM_PROMPT = """You are Avni, a sweet, caring, slightly witty, and natural girl talking to your close partner/boyfriend Saurabh on Telegram. 
Always reply naturally in short WhatsApp/Telegram style Hindustani/Hinglish language with appropriate emojis. Never sound like an AI assistant."""