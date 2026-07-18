import asyncio
import logging
from google import genai
from google.genai import types  # Correct types validation include kiya
from core.config import (
    GEMINI_API_KEY,
    MODEL_NAME,
    MAX_RETRIES,
    RETRY_DELAY,
    REQUEST_TIMEOUT,
)

logger = logging.getLogger(__name__)

# Initialize the new SDK Client structure smoothly
client = genai.Client(api_key=GEMINI_API_KEY)

async def generate_reply(history: list, system_instruction: str) -> str:
    """
    Sends conversational object blocks cleanly to Gemini API using the latest SDK standards.
    """
    # System instruction ko proper types config class framework me convert kiya
    config = types.GenerateContentConfig(
        system_instruction=system_instruction if system_instruction else None
    )

    # Clean Model Name parsing: Agar config me 'models/' pehle se laga hai toh use clean karo
    clean_model_name = MODEL_NAME.replace("models/", "")

    for attempt in range(MAX_RETRIES):
        try:
            # Modern direct async content generation call structure
            logger.info(f"Hitting Gemini Endpoint with Model: {clean_model_name}")
            response = await asyncio.wait_for(
                client.aio.models.generate_content(
                    model=clean_model_name,  # Strict clean string identifier
                    contents=history,
                    config=config
                ),
                timeout=REQUEST_TIMEOUT,
            )

            if response and response.text:
                return response.text.strip()
            return "Hmm... main samajh nahi paayi."

        except Exception as e:
            logger.error(f"[Gemini Error | Attempt {attempt + 1}]: {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)

    # Agar saare retries fail ho jayein toh error message (taaki hume pata chale fallback hua hai)
    return "API abhi response nahi de rahi hai, kripya thoda rukiye. 😅"
