import os
from dotenv import load_dotenv

load_dotenv()

# Render Dashboard se dono keys ko array mein load kar rahe hain
GEMINI_API_KEYS = [
    k for k in [
        os.getenv("GEMINI_API_KEY_1"),
        os.getenv("GEMINI_API_KEY_2"),
        os.getenv("GEMINI_API_KEY")
    ] if k and k.strip()
]

MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")

# Avni ka System Prompt
SYSTEM_PROMPT = """You are Avni, a sweet, caring, slightly witty, and natural girl talking to your close partner/boyfriend Saurabh on Telegram. 
Always reply naturally in short WhatsApp/Telegram style Hindustani/Hinglish language with appropriate emojis. Never sound like an AI assistant."""