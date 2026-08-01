import re
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

# Strict Question Words: Agar sentence mein inme se koi word hai, toh Fact Extractor use REJECT kar dega
QUESTION_WORDS = {
    "kya", "kab", "kahan", "kaise", "kyun", "kon", "konsa", "konsi", "kis",
    "what", "when", "where", "why", "who", "which", "how"
}

# Generic Noise words to strip from values
NOISE_WORDS = {"bahut", "bohot", "bhut", "bhi", "hi", "toh", "to", "batao", "batayein", "pata"}

# Pre-defined Lists for High-Accuracy Strict Matching
KNOWN_COLORS = ["blue", "black", "red", "green", "white", "yellow", "pink", "purple", "orange", "grey", "gray"]
KNOWN_DRINKS = ["cold coffee", "coffee", "tea", "chai", "green tea", "latte", "cappuccino", "juice", "beer", "wine"]

FACT_PATTERNS = [
    # 1. Birthday Pattern (Strict date/month capture)
    (r"(?:mera\s+)?birthday\s+(?:kab\s+aata\s+hai|hai)?\s*([0-9]{1,2}(?:\s+[a-zA-Z]+|\/[0-9]{1,2}|-[0-9]{1,2}))", "birthday", "profile", 100),

    # 2. Specific Preferences - Drinks
    (r"(?:mujhe|meri)\s+(?:favourite|favorite|pasand)\s+(?:drink|coffee|tea|chai)\s+([a-zA-Z\s]+?)(?:\s+bahut|\s+bohot|\s+hai|\.|$)", "favorite_drink", "preference", 90),
    (r"([a-zA-Z\s]+)\s+(?:bohot\s+|bahut\s+)?pasand\s+hai", "favorite_drink", "preference", 80),

    # 3. Specific Preferences - Colors
    (r"(?:mera|meri)\s+(?:favourite|favorite)\s+(?:color|colour|rang)\s+([a-zA-Z]+)", "favorite_color", "preference", 90),

    # 4. Work/Profession (Only matches affirmative statements like "Main X me kaam karta hoon")
    (r"(?:main|me)\s+([a-zA-Z\s]+?)\s+(?:me\s+)?(?:kaam|job|work)\s+(?:karta|karti)\s+hoon", "profession", "profile", 90),

    # 5. Names
    (r"mera\s+naam\s+([a-zA-Z]+)\s+hai", "user_name", "profile", 95),
]

def _is_question(text: str) -> bool:
    """Checks if the sentence is a question to avoid saving questions as facts."""
    clean = text.lower().strip()
    if "?" in clean:
        return True
    words = set(re.findall(r'\b\w+\b', clean))
    return bool(words & QUESTION_WORDS)

def _clean_value(val: str) -> str:
    """Strips noise words from extracted values."""
    words = val.strip().split()
    cleaned = [w for w in words if w.lower() not in NOISE_WORDS]
    return " ".join(cleaned).strip()

def extract_ranked_facts(text: str) -> List[Tuple[str, str, str, int]]:
    """
    Parses incoming user message and returns a LIST of all detected ranked facts.
    """
    extracted_facts = []
    if not text or not text.strip():
        return extracted_facts

    clean_text = text.strip()

    # CRITICAL CHECK: Ignore questions completely from fact extraction!
    if _is_question(clean_text):
        logger.info("[FACT RANKING]: Question detected. Skipping fact extraction for: '%s'", clean_text)
        return extracted_facts

    seen_keys = set()

    # --- DIRECT DICTIONARY LOOKUPS FOR HIGH ACCURACY ---
    lower_text = clean_text.lower()

    # Color Direct Lookup
    for color in KNOWN_COLORS:
        if re.search(rf"\b{color}\b", lower_text) and any(w in lower_text for w in ["color", "colour", "rang", "favourite", "favorite"]):
            extracted_facts.append(("favorite_color", color.capitalize(), "preference", 90))
            seen_keys.add("favorite_color")
            break

    # Drink Direct Lookup
    for drink in KNOWN_DRINKS:
        if drink in lower_text and any(w in lower_text for w in ["pasand", "favourite", "favorite", "drink", "peena"]):
            if "favorite_drink" not in seen_keys:
                extracted_facts.append(("favorite_drink", drink.title(), "preference", 90))
                seen_keys.add("favorite_drink")
                break

    # --- REGEX PATTERN MATCHING ---
    for item in FACT_PATTERNS:
        pattern, default_key, fact_type, importance = item[0], item[1], item[2], item[3]

        if default_key in seen_keys:
            continue

        matches = re.finditer(pattern, clean_text, re.IGNORECASE)
        for match in matches:
            groups = match.groups()
            if len(groups) == 1:
                val = _clean_value(groups[0])
                val_words = set(val.lower().split())

                # Final validation before appending
                if val and not (val_words & QUESTION_WORDS):
                    extracted_facts.append((default_key, val, fact_type, importance))
                    seen_keys.add(default_key)
                    break

    if extracted_facts:
        logger.info("[FACT RANKING EXTRACTED]: Found %d facts in message.", len(extracted_facts))

    return extracted_facts