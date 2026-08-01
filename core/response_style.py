import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_style_controls(primary_mood: str) -> Dict[str, Any]:
    """
    Generates strict style parameters for the LLM based on active emotional atmosphere.
    """
    if primary_mood in ["SUPPORTIVE", "SAD", "SERIOUS"]:
        return {
            "max_words": 12,
            "emoji_frequency": "Avoid emojis (0%)",
            "humor_enabled": False,
            "teasing_enabled": False,
            "energy_level": "Low",
            "pace": "Slow & Thoughtful"
        }
    elif primary_mood == "PLAYFUL":
        return {
            "max_words": 15,
            "emoji_frequency": "Subtle (Rare - 20% max)",
            "humor_enabled": True,
            "teasing_enabled": True,
            "energy_level": "High",
            "pace": "Fast & Relaxed"
        }
    else:  # FRIENDLY_CASUAL
        return {
            "max_words": 10,
            "emoji_frequency": "Very Rare (1 in 5 messages)",
            "humor_enabled": True,
            "teasing_enabled": False,
            "energy_level": "Moderate",
            "pace": "Natural"
        }