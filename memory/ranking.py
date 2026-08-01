import re
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

# Words that indicate a question, not a real user preference
QUESTION_STOP_WORDS = {"kya", "kab", "kahan", "kaise", "kyun", "kon", "what", "when", "where", "why", "who"}

FACT_PATTERNS = [
    # Birthday Variations
    (r"(?:mera\s+)?birthday\s+(?:kab\s+aata\s+hai|hai)?\s*([0-9]{1,2}(?:\s+[a-zA-Z]+|\/[0-9]{1,2}|-[0-9]{1,2}))", "birthday", "profile", 100),
    (r"birthday\s+([0-9]{1,2}(?:\s+[a-zA-Z]+|\/[0-9]{1,2}|-[0-9]{1,2}))", "birthday", "profile", 100),
    
    # Specific Preferences
    (r"(?:mujhe|meri)\s+(?:favourite|favorite|pasand)\s+(drink|coffee|tea|chai)\s+([a-zA-Z\s]+)\s+hai", "favorite_drink", "preference", 90),
    (r"(?:mujhe|meri)\s+(?:favourite|favorite|pasand)\s+(color|rang)\s+([a-zA-Z\s]+)\s+hai", "favorite_color", "preference", 90),
    (r"(?:mujhe|meri)\s+(?:favourite|favorite|pasand)\s+(game|khel)\s+([a-zA-Z0-9\s]+)\s+hai", "favorite_game", "preference", 90),
    
    # General Preferences
    (r"(?:mujhe|meri)\s+(?:favourite|favorite)\s+([a-zA-Z\s]+)\s+hai", "preference_general", "preference", 85),
    (r"([a-zA-Z\s]+)\s+(?:bohot\s+)?pasand\s+hai", "preference_general", "preference", 80),
    
    # Work/Profession
    (r"(?:main|me)\s+([a-zA-Z\s]+)\s+(?:me\s+)?(?:kaam|job|work)\s+(?:karta|karti)\s+hoon", "profession", "profile", 90),
    
    # Names
    (r"mera\s+naam\s+([a-zA-Z]+)\s+hai", "user_name", "profile", 95),
]

def extract_ranked_facts(text: str) -> List[Tuple[str, str, str, int]]:
    extracted_facts = []
    if not text or not text.strip():
        return extracted_facts

    clean_text = text.strip()

    for item in FACT_PATTERNS:
        pattern, default_key, fact_type, importance = item[0], item[1], item[2], item[3]

        matches = re.finditer(pattern, clean_text, re.IGNORECASE)
        for match in matches:
            groups = match.groups()
            
            if len(groups) == 1:
                val = groups[0].strip()
                # Ignore question words from being saved as facts
                if val.lower() not in QUESTION_STOP_WORDS:
                    extracted_facts.append((default_key, val, fact_type, importance))
                    
            elif len(groups) >= 2:
                specific_sub = groups[0].strip().lower()
                val = groups[1].strip()
                
                # Filter out values that contain question words
                if not any(qw in val.lower().split() for qw in QUESTION_STOP_WORDS):
                    fact_key = f"favorite_{specific_sub}" if "favorite" not in specific_sub else specific_sub
                    extracted_facts.append((fact_key, val, fact_type, importance))

    if extracted_facts:
        logger.info("[FACT RANKING EXTRACTED]: Found %d facts in message.", len(extracted_facts))

    return extracted_facts