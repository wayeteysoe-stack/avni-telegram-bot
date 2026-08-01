import re
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

# Stop words and Question markers that must NEVER be saved as facts
QUESTION_STOP_WORDS = {
    "kya", "kab", "kahan", "kaise", "kyun", "kon", "konsa", "konsi",
    "what", "when", "where", "why", "who", "which", "how"
}

NOISE_WORDS = {"bahut", "bohot", "bhut", "bhi", "hi", "toh", "to", "vazahat", "batao", "batayein"}

FACT_PATTERNS = [
    # 1. Consolidated Birthday Pattern (Fixes Duplicate Extraction)
    (r"(?:mera\s+)?birthday\s+(?:kab\s+aata\s+hai|hai)?\s*([0-9]{1,2}(?:\s+[a-zA-Z]+|\/[0-9]{1,2}|-[0-9]{1,2}))", "birthday", "profile", 100),

    # 2. Specific Preferences (Tightened value extraction)
    (r"(?:mujhe|meri)\s+(?:favourite|favorite|pasand)\s+(drink|coffee|tea|chai)\s+([a-zA-Z\s]+?)(?:\s+bahut|\s+bohot|\s+hai|\.|$)", "favorite_drink", "preference", 90),
    (r"(?:mujhe|meri)\s+(?:favourite|favorite|pasand)\s+(color|rang)\s+([a-zA-Z\s]+?)(?:\s+bahut|\s+bohot|\s+hai|\.|$)", "favorite_color", "preference", 90),
    (r"(?:mujhe|meri)\s+(?:favourite|favorite|pasand)\s+(game|khel)\s+([a-zA-Z0-9\s]+?)(?:\s+bahut|\s+bohot|\s+hai|\.|$)", "favorite_game", "preference", 90),

    # 3. General Preferences
    (r"(?:mujhe|meri)\s+(?:favourite|favorite)\s+([a-zA-Z\s]+?)\s+hai", "preference_general", "preference", 85),
    (r"([a-zA-Z\s]+?)\s+(?:bohot\s+|bahut\s+)?pasand\s+hai", "preference_general", "preference", 80),

    # 4. Work/Profession
    (r"(?:main|me)\s+([a-zA-Z\s]+?)\s+(?:me\s+)?(?:kaam|job|work)\s+(?:karta|karti)\s+hoon", "profession", "profile", 90),

    # 5. Names
    (r"mera\s+naam\s+([a-zA-Z]+)\s+hai", "user_name", "profile", 95),
]

def _clean_value(val: str) -> str:
    """Removes trailing noise words like 'bahut', 'bohot', etc."""
    words = val.strip().split()
    cleaned = [w for w in words if w.lower() not in NOISE_WORDS]
    return " ".join(cleaned).strip()

def extract_ranked_facts(text: str) -> List[Tuple[str, str, str, int]]:
    extracted_facts = []
    if not text or not text.strip():
        return extracted_facts

    clean_text = text.strip()
    seen_keys = set()  # Deduplication during same message parsing

    for item in FACT_PATTERNS:
        pattern, default_key, fact_type, importance = item[0], item[1], item[2], item[3]

        matches = re.finditer(pattern, clean_text, re.IGNORECASE)
        for match in matches:
            groups = match.groups()

            if len(groups) == 1:
                val = _clean_value(groups[0])
                if val and val.lower() not in QUESTION_STOP_WORDS:
                    if default_key not in seen_keys:
                        extracted_facts.append((default_key, val, fact_type, importance))
                        seen_keys.add(default_key)

            elif len(groups) >= 2:
                specific_sub = groups[0].strip().lower()
                val = _clean_value(groups[1])

                # Reject if extracted value contains or is a question word
                val_words = set(val.lower().split())
                if val and not (val_words & QUESTION_STOP_WORDS):
                    fact_key = f"favorite_{specific_sub}" if "favorite" not in specific_sub else specific_sub
                    if fact_key not in seen_keys:
                        extracted_facts.append((fact_key, val, fact_type, importance))
                        seen_keys.add(fact_key)

    if extracted_facts:
        logger.info("[FACT RANKING EXTRACTED]: Found %d facts in message.", len(extracted_facts))

    return extracted_facts