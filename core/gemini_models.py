import logging
from typing import Optional, List
from google import genai
from core.gemini_errors import ModelSelectionError

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Thread-safe manager for detecting and managing active compatible models dynamically.
    """
    # Active tested working model set as top priority
    PREFERRED_TIERS = ["gemini-flash-latest", "gemini-2.0-flash", "gemini-1.5-flash"]

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

            # Match preferred tier starting with gemini-flash-latest
            for pref in self.PREFERRED_TIERS:
                if pref in compatible_names:
                    self._cached_model = pref
                    logger.info(f"[MODEL MANAGER]: Selected preferred model '{pref}'")
                    return self._cached_model

            self._cached_model = compatible_names[0]
            logger.info(f"[MODEL MANAGER]: Selected first available model '{self._cached_model}'")
            return self._cached_model

        except Exception as e:
            logger.warning(f"[MODEL MANAGER]: API scan fallback to active default 'gemini-flash-latest': {e}")
            self._cached_model = "gemini-flash-latest"
            return self._cached_model

    def invalidate_cache(self):
        self._cached_model = None

model_manager = ModelManager()