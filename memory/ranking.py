import re
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

# Pattern Rules: (Regex, Default Key, Type, Importance)
FACT_PATTERNS = [
    # Birthday Variations (14 March, 14 Mar, 14/03, 14-03)
    (r"(?:mera\s+)?birthday\s+(?:kab\s+aata\s+hai|hai)?\s*([0-9]{1,2}(?:\s+[a-zA-Z]+|\/[0-9]{1,2}|-[0-9]{1,2}))", "birthday", "profile", 100),
    (r"birthday\s+([0-9]{1,2}(?:\s+[a-zA-Z]+|\/[0-9]{1,2}|-[0-9]{1,2}))", "birthday", "profile", 100),
    
    # Specific Preferences
    (r"(?:mujhe|meri)\s+(?:favourite|favorite|pasand)\s+(drink|coffee|tea|chai)\s+([a-zA-Z\s]+)\s+hai", "favorite_drink", "preference", 90),
    (r"(?:mujhe|meri)\s+(?:favourite|favorite|pasand)\s+(color|rang)\s+([a-zA-Z\s]+)\s+hai", "favorite_color", "preference", 90),
    (r"(?:mujhe|meri)\s+(?:favourite|favorite|pasand)\s+(game|khel)\s+([a-zA-Z0-9\s]+)\s+hai", "favorite_game", "preference", 90),
    
    # General Preferences (Fallback)
    (r"(?:mujhe|meri)\s+(?:favourite|favorite)\s+([a-zA-Z\s]+)\s+hai", "preference_general", "preference", 85),
    (r"([a-zA-Z\s]+)\s+(?:bohot\s+)?pasand\s+hai", "preference_general", "preference", 80),
    
    # Work/Profession (Gender Neutral: karta/karti/job/work)
    (r"(?:main|me)\s+([a-zA-Z\s]+)\s+(?:me\s+)?(?:kaam|job|work)\s+(?:karta|karti)\s+hoon", "profession", "profile", 90),
    
    # Names
    (r"mera\s+naam\s+([a-zA-Z]+)\s+hai", "user_name", "profile", 95),
]

def extract_ranked_facts(text: str) -> List[Tuple[str, str, str, int]]:
    """
    Parses incoming user message and returns a LIST of all detected ranked facts.
    Returns: [(fact_key, fact_value, fact_type, importance_score), ...]
    """
    extracted_facts = []
    if not text or not text.strip():
        return extracted_facts

    clean_text = text.strip()

    for item in FACT_PATTERNS:
        pattern = item[0]
        default_key = item[1]
        fact_type = item[2]
        importance = item[3]

        matches = re.finditer(pattern, clean_text, re.IGNORECASE)
        for match in matches:
            groups = match.groups()
            if len(groups) == 1:
                val = groups[0].strip()
                extracted_facts.append((default_key, val, fact_type, importance))
            elif len(groups) >= 2:
                # Dynamic key mapping if specific sub-type matched (e.g. favorite drink)
                specific_sub = groups[0].strip().lower()
                val = groups[1].strip()
                fact_key = f"favorite_{specific_sub}" if "favorite" not in specific_sub else specific_sub
                extracted_facts.append((fact_key, val, fact_type, importance))

    if extracted_facts:
        logger.info("[FACT RANKING EXTRACTED]: Found %d facts in message.", len(extracted_facts))

    return extracted_facts