import logging
import random
from google import genai
from google.genai import types
from core.config import GEMINI_API_KEYS, MODEL_NAME, SYSTEM_PROMPT

logger = logging.getLogger(__name__)

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
    if not GEMINI_API_KEYS:
        logger.error("[Gemini Error]: No API keys available in environment!")
        return random.choice(DYNAMIC_FALLBACKS)

    # Format memory/history
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

    # Add current user text
    formatted_contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=str(user_text).strip())]
        )
    )

    # Loop through available API Keys (Rotation on failure)
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
            logger.warning(f"[API Key #{index+1} Hit Error]: {err_str}")
            
            # Agar 429 quota error aaye, to silently agli key par switch ho jao
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                logger.info(f"Key #{index+1} quota exhausted. Rotating to next key...")
                continue
            
            if index == len(GEMINI_API_KEYS) - 1:
                return random.choice(DYNAMIC_FALLBACKS)

    return random.choice(DYNAMIC_FALLBACKS)