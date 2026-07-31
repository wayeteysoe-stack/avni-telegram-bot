import logging
import asyncio
import random
from typing import List, Dict, Any
from core.gemini_client import client_pool
from core.gemini_models import model_manager
from core.context_builder import build_gemini_contents
from core.prompt import SYSTEM_PROMPT
from google.genai import types

logger = logging.getLogger(__name__)

TRANSIENT_ERRORS = [
    "408", "500", "502", "503", "504", 
    "timeout", "timed out", "connection reset", "network"
]

FALLBACK_RESPONSES = [
    "Arey mera internet thoda hagne laga hai 🤦‍♀️ ek sec...",
    "Acha ek min ruko, network issue de raha hai mera.",
    "Hmm... tumhara message poora nahi aaya mere paas 🤔",
    "Arey net slow ho gaya ekdam se, kya bola tumne?"
]

# FIX: Pure synchronous function for thread executor (NO async keyword)
def _call_gemini_sync(client, model_name, contents, system_instruction):
    """Executes the synchronous GenAI SDK call inside a separate thread."""
    return client.models.generate_content(
        model=model_name,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.85,
        )
    )

async def generate_reply_with_context(contents: list, system_instruction: str) -> str:
    """
    Primary non-blocking async interface for Phase 2.
    """
    active_clients = client_pool.get_active_clients()

    if not active_clients:
        logger.error("[GEMINI SERVICE]: Zero valid API clients available in pool.")
        return random.choice(FALLBACK_RESPONSES)

    for client_info in active_clients:
        var_name = client_info["var_name"]
        client = client_info["client"]

        try:
            model_name = model_manager.get_compatible_model(client)
        except Exception as e:
            logger.error(f"[GEMINI SERVICE]: Could not resolve model for {var_name}: {e}")
            continue

        for attempt in range(1, 3):
            try:
                # Thread executor running synchronous SDK call
                response = await asyncio.to_thread(
                    _call_gemini_sync, client, model_name, contents, system_instruction
                )

                if response and response.text:
                    return response.text.strip()

            except Exception as e:
                err_msg = str(e).lower()
                logger.warning(f"[GEMINI SERVICE]: Key {var_name} (Attempt {attempt}) Error: {e}")

                if "429" in err_msg or "resource_exhausted" in err_msg:
                    logger.info(f"[GEMINI SERVICE]: Key {var_name} quota hit. Rotating to next key...")
                    break

                if "not_found" in err_msg and ("model" in err_msg or "models/" in err_msg):
                    logger.warning(f"[GEMINI SERVICE]: Model NotFound detected. Invalidating cache...")
                    model_manager.invalidate_cache()
                    try:
                        model_name = model_manager.get_compatible_model(client)
                    except Exception:
                        break

                if any(err in err_msg for err in TRANSIENT_ERRORS):
                    await asyncio.sleep(attempt * 1.5)
                    continue

                break

    logger.error("[GEMINI SERVICE]: All valid keys exhausted or attempts failed.")
    return random.choice(FALLBACK_RESPONSES)


async def generate_reply(user_text: str, conversation_history: List[Dict[str, Any]] = None) -> str:
    """Backward compatibility fallback wrapper."""
    contents = build_gemini_contents(user_text, conversation_history)
    return await generate_reply_with_context(contents, SYSTEM_PROMPT)