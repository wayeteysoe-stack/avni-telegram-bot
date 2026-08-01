import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_relationship_context(interaction_count: int, days_known: int = 1) -> Dict[str, Any]:
    """
    Calculates relationship stage and familiarity parameters.
    """
    if interaction_count < 10:
        stage = "NEW_ACQUAINTANCE"
        vibe = "Polite, slightly reserved, warm but respectful."
        flirting = "Disabled"
        teasing_limit = "Low"
    elif interaction_count < 50:
        stage = "COMFORTABLE_FRIEND"
        vibe = "Warm, open, playful, occasionally teasing."
        flirting = "Subtle"
        teasing_limit = "Moderate"
    else:
        stage = "CLOSE_COMPANION"
        vibe = "Deep trust, highly comfortable, relaxed, authentic."
        flirting = "Natural"
        teasing_limit = "Comfortable"

    return {
        "stage": stage,
        "vibe_description": vibe,
        "flirting_allowed": flirting,
        "teasing_limit": teasing_limit
    }