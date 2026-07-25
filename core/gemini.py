import logging
import random
from google import genai
from google.genai import types
from core.config import GEMINI_API_KEY, MODEL_NAME, SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Initialize GenAI Client
client = genai.Client(api_key=GEMINI_API_KEY)

# Dynamic Human Fallbacks
DYNAMIC_FALLBACKS = [
    "Arey mera internet thoda hagne laga hai 🤦‍♀️ ek sec...",
    "Acha ek min ruko, wifi issue de raha hai mera.",
    "Hmm... tumhara message poora nahi aaya mere paas 🤔",
    "Arey net slow ho gaya ekdam se, kya bola tumne?",
    "Wait, msg deliver nhi ho rha tha proper 🙈 dubara bolo?"
]

def _extract_text_strictly(raw_data) -> str:
    """Helper function to convert any nested structure safely to string."""
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
    Async wrapper for generating Avni's response with strict string validation.
    """
    try:
        formatted_contents = []

        # Convert raw history items into strictly validated google.genai Content objects
        if conversation_history:
            for item in conversation_history:
                if isinstance(item, dict):
                    role = item.get("role", "user")
                    clean_text = _extract_text_strictly(item.get("parts", ""))
                    if clean_text.strip():
                        formatted_contents.append(
                            types.Content(
                                role=role,
                                parts=[types.Part.from_text(text=clean_text.strip())]
                            )
                        )
                elif isinstance(item, str) and item.strip():
                    formatted_contents.append(
                        types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=item.strip())]
                        )
                    )

        # Add current user prompt
        formatted_contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=str(user_text).strip())]
            )
        )

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
        else:
            return random.choice(DYNAMIC_FALLBACKS)

    except Exception as e:
        logger.error(f"[Gemini Core Fix Error]: {e}")
        return random.choice(DYNAMIC_FALLBACKS)