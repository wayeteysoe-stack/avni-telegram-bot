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

async def generate_reply(user_text: str, conversation_history: list = None) -> str:
    """
    Bulletproof Async wrapper for Avni's response using direct Contents API.
    """
    try:
        formatted_contents = []

        # Safe construction of history to prevent SDK Schema errors
        if conversation_history:
            for item in conversation_history:
                if isinstance(item, dict):
                    role = item.get("role", "user")
                    # Force string extraction
                    parts = item.get("parts", "")
                    if isinstance(parts, list):
                        parts_str = " ".join([str(p.get("text", p) if isinstance(p, dict) else p) for p in parts])
                    else:
                        parts_str = str(parts)

                    if parts_str.strip():
                        formatted_contents.append(
                            types.Content(
                                role="user" if role == "user" else "model",
                                parts=[types.Part.from_text(text=parts_str.strip())]
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
        logger.error(f"[Gemini Permanent Fix Error]: {e}")
        return random.choice(DYNAMIC_FALLBACKS)