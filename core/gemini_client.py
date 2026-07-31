import os
import logging
from typing import List, Dict, Any
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class GeminiClientPool:
    """
    Loads API keys deterministically, validates them with actual active API calls,
    and maintains an active pool of valid GenAI clients.
    """
    def __init__(self):
        self.clients: List[Dict[str, Any]] = []
        self.reload_and_validate()

    def _get_sorted_key_vars(self) -> List[str]:
        env_keys = [k for k in os.environ.keys() if k.startswith("GEMINI_API_KEY")]
        return sorted(env_keys)

    def reload_and_validate(self):
        self.clients.clear()
        sorted_vars = self._get_sorted_key_vars()

        for var_name in sorted_vars:
            key_val = os.environ.get(var_name, "").strip()
            if not key_val:
                continue

            try:
                client = genai.Client(api_key=key_val)
                # Active validation: Actual token counting call to verify API key authorization
                client.models.count_tokens(
                    model="gemini-1.5-flash", 
                    contents=[types.Content(role="user", parts=[types.Part.from_text(text="ping")])]
                )
                
                self.clients.append({
                    "var_name": var_name,
                    "key": key_val,
                    "client": client
                })
                logger.info(f"[CLIENT POOL]: Successfully validated key via active API ping: {var_name}")
            except Exception as e:
                logger.error(f"[CLIENT POOL ERROR]: Active API Key validation failed for {var_name}: {e}")

    def get_active_clients(self) -> List[Dict[str, Any]]:
        return self.clients

client_pool = GeminiClientPool()