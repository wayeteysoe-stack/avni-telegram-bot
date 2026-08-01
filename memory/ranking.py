import re
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

# --- STAGE 1: INTENT CLASSIFICATION (Question vs Statement) ---

# Strict Question Words (Enclosed in word boundaries \b to avoid sub-word matching like 'kisaan')
QUESTION_WORDS_REGEX = r"\b(?:kya|kab|kahan|kaise|kyun|kon|konsa|konsi|kis|what|when|where|why|who|which|how)\b"

def _is_question_intent(text: str) -> bool:
    """Classifies whether the user input is a question/query."""
    clean = text.lower().strip()
    
    # Direct Question Mark
    if "?" in clean:
        return True
        
    # Interrogative Word Pattern Match
    if re.search(QUESTION_WORDS_REGEX, clean):
        return True
        
    return False


# --- STAGE 2: ENTITY & SLOT EXTRACTION ---

# Known entity dictionaries for fast verification
KNOWN_COLORS = {
    "black", "blue", "red", "green", "white", "yellow", "pink", "purple", 
    "orange", "grey", "gray", "dark blue", "sky blue", "navy blue"
}

KNOWN_DRINKS = {
    "cold coffee", "coffee", "tea", "chai", "green tea", "latte", 
    "cappuccino", "juice", "beer", "wine", "mojito", "pepsi", "coke", 
    "red bull", "lemon soda", "soda", "water"
}

# Regex Entities
BIRTHDAY_REGEX = r"(?:mera\s+)?birthday\s+(?:kab\s+aata\s+hai|hai)?\s*([0-9]{1,2}(?:\s+[a-zA-Z]+|\/[0-9]{1,2}|-[0-9]{1,2}))"

PROFESSION_REGEX = r"(?:main|me|i\s+am\s+a|i\'m\s+a)\s+([a-zA-Z0-9\s]+?)\s*(?:me\s+kaam\s+karta\s+hoon|me\s+kaam\s+karti\s+hoon|hoon|hu|engineer|developer|analyst)?$"

def _normalize_title(val: str) -> str:
    """Proper Title Case capitalization (e.g., 'dark blue' -> 'Dark Blue')."""
    return " ".join([w.capitalize() for w in val.strip().split()])


def extract_ranked_facts(text: str) -> List[Tuple[str, str, str, int]]:
    """
    Primary Intent + Entity Classification Extraction Pipeline.
    Returns: [(fact_key, fact_value, fact_type, importance_score), ...]
    """
    extracted_facts = []
    if not text or not text.strip():
        return extracted_facts

    clean_text = text.strip()
    lower_text = clean_text.lower()

    # STEP 1: INTENT CLASSIFICATION
    if _is_question_intent(clean_text):
        logger.info("[INTENT CLASSIFIER]: Identified Question/Query. Rejection applied for: '%s'", clean_text)
        return []

    seen_keys = set()

    # STEP 2: ENTITY EXTRACTION

    # A. Birthday Extraction
    bday_match = re.search(BIRTHDAY_REGEX, clean_text, re.IGNORECASE)
    if bday_match:
        val = bday_match.group(1).strip()
        extracted_facts.append(("birthday", _normalize_title(val), "profile", 100))
        seen_keys.add("birthday")

    # B. Color Entity Extraction (Requires Context + Entity)
    has_color_context = any(w in lower_text for w in ["color", "colour", "rang"])
    if has_color_context:
        for color in KNOWN_COLORS:
            if re.search(rf"\b{color}\b", lower_text):
                extracted_facts.append(("favorite_color", _normalize_title(color), "preference", 90))
                seen_keys.add("favorite_color")
                break

    # C. Drink Entity Extraction (Requires Drink Match + Preference Context)
    has_drink_context = any(w in lower_text for w in ["pasand", "favourite", "favorite", "drink", "peena", "like", "love"])
    if has_drink_context:
        for drink in KNOWN_DRINKS:
            if re.search(rf"\b{drink}\b", lower_text):
                extracted_facts.append(("favorite_drink", _normalize_title(drink), "preference", 90))
                seen_keys.add("favorite_drink")
                break

    # D. Profession Entity Extraction
    if "profession" not in seen_keys:
        prof_match = re.search(r"(?:main|me)\s+([a-zA-Z0-9\s]+?)\s+(?:me\s+)?(?:kaam|job|work)\s+(?:karta|karti)\s+hoon", clean_text, re.IGNORECASE)
        if not prof_match:
            prof_match = re.search(r"(?:main|me|i\s+am\s+a)\s+([a-zA-Z0-9\s]+?)\s+(?:hoon|hu|engineer|developer|analyst)", clean_text, re.IGNORECASE)

        if prof_match:
            prof_val = prof_match.group(1).strip()
            # Stop Words Check for Professions
            if prof_val.lower() not in {"ek", "ekdam", "a", "an", "kisaan"} and len(prof_val.split()) <= 4:
                extracted_facts.append(("profession", _normalize_title(prof_val), "profile", 90))
                seen_keys.add("profession")

    # E. Name Extraction
    name_match = re.search(r"mera\s+naam\s+([a-zA-Z]+)\s+hai", clean_text, re.IGNORECASE)
    if name_match:
        name_val = name_match.group(1).strip()
        extracted_facts.append(("user_name", _normalize_title(name_val), "profile", 95))

    if extracted_facts:
        logger.info("[INTENT ENTITY EXTRACTED]: Found %d facts.", len(extracted_facts))

    return extracted_facts