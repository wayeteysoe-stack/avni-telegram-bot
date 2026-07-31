import logging
from typing import Optional, List
from google import genai
from core.gemini_errors import ModelSelectionError

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Thread-safe manager for detecting and managing active compatible models dynamically.
    """
    PREFERRED_TIERS = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]

    def __init__(self):
        self._cached_model: Optional[str] = None

    def get_compatible_model(self, client: genai.Client) -> str:
        if self._cached_model:
            return self._cached_model

        try:
            available_models = list(client.models.list())
            compatible_names: List[str] = []

            for m in available_models:
                methods = getattr(m, "supported_generation_methods", []) or []
                if "generateContent" in methods or not methods:
                    clean_name = m.name.replace("models/", "")
                    compatible_names.append(clean_name)

            if not compatible_names:
                raise ModelSelectionError("No models supporting 'generateContent' were found in API response.")

            # 1. Match preferred tiers
            for pref in self.PREFERRED_TIERS:
                if pref in compatible_names:
                    self._cached_model = pref
                    logger.info(f"[MODEL MANAGER]: Selected preferred model '{pref}'")
                    return self._cached_model

            # 2. Dynamic fallback: Pick the first actual compatible model returned by API
            self._cached_model = compatible_names[0]
            logger.info(f"[MODEL MANAGER]: Selected first available compatible model '{self._cached_model}'")
            return self._cached_model

        except Exception as e:
            logger.error(f"[MODEL MANAGER ERROR]: Dynamic model detection failed: {e}")
            raise ModelSelectionError(f"Failed to query compatible models from API: {e}")

    def invalidate_cache(self):
        self._cached_model = None

model_manager = ModelManager()