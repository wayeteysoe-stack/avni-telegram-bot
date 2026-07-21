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
    Async wrapper for generating Avni's response using the Gemini API.
    """
    try:
        contents = []
        if conversation_history:
            for msg in conversation_history:
                contents.append(msg)
        
        contents.append(user_text)

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
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