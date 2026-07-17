# avni-bot/core/gemini.py
import asyncio
from google import genai
from core.config import (
    GEMINI_API_KEY,
    MODEL_NAME,
    MAX_RETRIES,
    RETRY_DELAY,
    REQUEST_TIMEOUT,
)

# Initialize the new SDK Client structure smoothly
client = genai.Client(api_key=GEMINI_API_KEY)

async def generate_reply(history: list, system_instruction: str) -> str:
    """
    Sends conversational object blocks cleanly to Gemini API using the latest SDK standards.
    """
    for attempt in range(MAX_RETRIES):
        try:
            # New direct configuration pass framework for modern google-genai versions
            response = await asyncio.wait_for(
                client.aio.models.generate_content(
                    model=MODEL_NAME,
                    contents=history,
                    config={
                        "system_instruction": system_instruction,
                    }
                ),
                timeout=REQUEST_TIMEOUT,
            )

            if response and response.text:
                return response.text.strip()
            return "Hmm..."

        except Exception as e:
            print(f"[Gemini Error | Attempt {attempt + 1}]: {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)

    return "Arey ek min yrr 😅"