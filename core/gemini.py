# avni-bot/core/gemini.py
import asyncio
import logging
from google import genai
from google.genai import types
from core.config import (
    GEMINI_API_KEY,
    MODEL_NAME,
    MAX_RETRIES,
    RETRY_DELAY,
    REQUEST_TIMEOUT,
)

logger = logging.getLogger(__name__)

# 🌟 FORCE V1 PRODUCTION API ENDPOINT (Bypasses the buggy v1beta 404 routing route completely)
try:
    client = genai.Client(
        api_key=GEMINI_API_KEY,
        http_options={"api_version": "v1"}
    )
except Exception as e:
    logger.critical(f"Gemini Client Core Initialization Failed: {e}")
    client = None

async def generate_reply(history: list, system_instruction: str) -> str:
    """
    Latest SDK standards ke mutabik cleanly stable v1 endpoint par content generate karta hai.
    """
    if not client:
        return "Internal Technical Error: AI core ready nahi hai. 🥺"

    # System instruction ko valid types config framework me map kiya
    config = types.GenerateContentConfig(
        system_instruction=system_instruction if system_instruction else None,
        temperature=0.7,  # Human conversational warmth match karne ke liye
        top_p=0.95
    )

    # Absolute Model name extraction logic
    clean_model_name = MODEL_NAME.replace("models/", "").strip()

    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Targeting Clean Model Endpoint: {clean_model_name} (Attempt {attempt + 1})")
            
            # Direct non-blocking async payload dispatch pipeline
            response = await asyncio.wait_for(
                client.aio.models.generate_content(
                    model=clean_model_name,
                    contents=history,
                    config=config
                ),
                timeout=REQUEST_TIMEOUT,
            )

            if response and response.text:
                return response.text.strip()
            return "Hmm... main samajh nahi paayi. Dobara bolo? 🤷‍♀️"

        except Exception as e:
            logger.error(f"[Gemini Core Engine Error | Attempt {attempt + 1}]: {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)

    return "API abhi response nahi de rahi hai, network slow hai shayad. Kripya thoda rukiye! 😅"
