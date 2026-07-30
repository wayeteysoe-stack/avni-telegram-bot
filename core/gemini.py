import logging
import random
from google import genai
from google.genai import types
from core.config import GEMINI_API_KEYS, MODEL_NAME, SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Fallback messages
DYNAMIC_FALLBACKS = [
    "Arey mera internet thoda hagne laga hai 🤦‍♀️ ek sec...",
    "Acha ek min ruko, wifi issue de raha hai mera.",
    "Hmm... tumhara message poora nahi aaya mere paas 🤔",
    "Arey net slow ho gaya ekdam se, kya bola tumne?",
    "Wait, msg deliver nhi ho rha tha proper 🙈 dubara bolo?"
]

def _extract_text_strictly(raw_data) -> str:
    if isinstance(raw_data, str):
        return raw_data
    if isinstance(raw_data, dict):
        if "text" in raw_data:
            return _extract_text_strictly(raw_data["text"])
        if "parts" in raw_data:
            return _extract_text_strictly(raw_data["parts"])
    if isinstance(raw_data, list):
        extracted = [_extract_text_strictly(item) for item in raw_data]
        return " ".join([e for e in extracted if e])
    return str(raw_data) if raw_data is not None else ""

async def generate_reply(user_text: str, conversation_history: list = None) -> str:
    """
    Tries generating content across multiple API keys until one succeeds.
    """
    if not GEMINI_API_KEYS:
        logger.error("[Gemini Core Error]: No API keys provided in configuration.")
        return random.choice(DYNAMIC_FALLBACKS)

    # Format conversation history
    formatted_contents = []
    if conversation_history:
        for item in conversation_history:
            if isinstance(item, dict):
                role = item.get("role", "user")
                clean_text = _extract_text_strictly(item.get("parts", ""))
                if clean_text.strip():
                    formatted_contents.append(
                        types.Content(
                            role="user" if role == "user" else "model",
                            parts=[types.Part.from_text(text=clean_text.strip())]
                        )
                    )

    # Add latest user prompt
    formatted_contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=str(user_text).strip())]
        )
    )

    # Loop through all available API Keys (Rotation)
    for index, api_key in enumerate(GEMINI_API_KEYS):
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=formatted_contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.85,
                )
            )
            
            if response and response.text:
                return response.text.strip()

        except Exception as e:
            err_str = str(e)
            logger.warning(f"[API Key {index+1} Failed]: {err_str}")
            
            # If rate limited (429), loop automatically moves to the next key!
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                logger.info(f"Switching from Key #{index+1} to next available key...")
                continue
            
            # For other errors on last key
            if index == len(GEMINI_API_KEYS) - 1:
                return random.choice(DYNAMIC_FALLBACKS)

    return random.choice(DYNAMIC_FALLBACKS)