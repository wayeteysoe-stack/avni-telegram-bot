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

# Force v1 production routing endpoint cleanly
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
    SDK payload constraints ko bypass karne ke liye system instructions ko 
    content array me insert karke model standard par cleanly generate karta hai.
    """
    if not client:
        return "Internal Technical Error: AI core ready nahi hai. 🥺"

    # 🌟 NEW PIPELINE RESOLUTION: JSON payload map block crash se bachne ke liye 
    # instructions ko safe content layer object banakar insert kiya.
    payload_contents = []
    
    if system_instruction:
        payload_contents.append({
            "role": "system",
            "parts": [{"text": system_instruction}]
        })
    
    # Baaki bachi hui user/model history safe append karo
    payload_contents.extend(history)

    # Config se buggy system_instruction parameter bilkul hata diya (Bypasses 400 Error)
    config = types.GenerateContentConfig(
        temperature=0.7,
        top_p=0.95
    )

    clean_model_name = MODEL_NAME.replace("models/", "").strip()

    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Targeting Secure JSON Payload on Model: {clean_model_name} (Attempt {attempt + 1})")
            
            # Direct async layout invocation
            response = await asyncio.wait_for(
                client.aio.models.generate_content(
                    model=clean_model_name,
                    contents=payload_contents,  # Structured injected payload
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
