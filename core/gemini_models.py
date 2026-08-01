import logging
from typing import Optional, List
from google import genai
from core.gemini_errors import ModelSelectionError

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Thread-safe manager for detecting active models.
    Scans API ONLY ONCE at startup and permanently caches the result.
    """
    PREFERRED_TIERS = ["gemini-flash-latest", "gemini-2.0-flash", "gemini-1.5-flash"]
    _cached_model: Optional[str] = "gemini-flash-latest"  # Instant Default
    _is_initialized: bool = False

    def get_compatible_model(self, client: genai.Client) -> str:
        # If model is already discovered, return immediately without API call
        if self._is_initialized and self._cached_model:
            return self._cached_model

        try:
            available_models = list(client.models.list())
            compatible_names: List[str] = []

            for m in available_models:
                methods = getattr(m, "supported_generation_methods", []) or []
                if "generateContent" in methods or not methods:
                    clean_name = m.name.replace("models/", "")
                    compatible_names.append(clean_name)

            for pref in self.PREFERRED_TIERS:
                if pref in compatible_names:
                    self._cached_model = pref
                    self._is_initialized = True
                    logger.info(f"[MODEL MANAGER]: Scanned & Cached model '{pref}'")
                    return self._cached_model

            if compatible_names:
                self._cached_model = compatible_names[0]

        except Exception as e:
            logger.warning(f"[MODEL MANAGER]: Discovery scan fallback to 'gemini-flash-latest': {e}")
            
        self._is_initialized = True
        return self._cached_model

    def invalidate_cache(self):
        self._is_initialized = False

model_manager = ModelManager()