# avni-bot/core/gemini.py
import logging
import concurrent.futures
from google import genai
from core.config import GEMINI_API_KEY, MODEL_NAME

logger = logging.getLogger(__name__)

# Strict stable production initialization
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    logger.critical(f"Gemini Client Core Initialization Failed: {e}")
    client = None

def generate_reply_sync(history: list, system_instruction: str) -> str:
    """
    Synchronous function jo Google API ko smooth native configuration call bhejti hai.
    """
    if not client:
        return "Internal Technical Error: AI core ready nahi hai. 🥺"

    clean_model_name = MODEL_NAME.replace("models/", "").strip()
    
    # Naye SDK ka direct configuration block jo v1 par safely execute hota hai
    response = client.models.generate_content(
        model=clean_model_name,
        contents=history,
        config={
            "system_instruction": system_instruction if system_instruction else None,
            "temperature": 0.7,
            "top_p": 0.95
        }
    )
    
    if response and response.text:
        return response.text.strip()
    return "Hmm... main samajh nahi paayi. Dobara bolo? 🤷‍♀️"

async def generate_reply(history: list, system_instruction: str) -> str:
    """
    Main Async wrapper jo thread pool me sync method ko chala kar 
    Telegram event loop ko crash hone se bachata hai.
    """
    import asyncio
    loop = asyncio.get_running_loop()
    
    try:
        # standard thread pool execute to bypass client.aio structural errors
        with concurrent.futures.ThreadPoolExecutor() as pool:
            bot_response = await loop.run_in_executor(
                pool, generate_reply_sync, history, system_instruction
            )
            return bot_response
    except Exception as e:
        logger.error(f"[Gemini Core Master Fix Error]: {e}")
        return "API abhi response nahi de rahi hai, kripya thoda rukiye! 😅"
