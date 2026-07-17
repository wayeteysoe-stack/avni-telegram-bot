# avni-bot/core/extractors.py
import re

def extract_profile(message: str) -> dict:
    """
    Extract basic profile information from a user's message with intent checks.
    """
    profile = {}
    text = message.lower().strip()

    # 1. Name Extraction (Handles spaces and ignores standard stop words)
    name_match = re.search(r"(?:mera\s+naam|my\s+name\s+is|i\s+am|i\'m)\s+([a-zA-Z\s]+?)(?:\s+hai|\.|$)", text, re.IGNORECASE)
    if name_match:
        extracted_name = name_match.group(1).strip()
        stop_words = ["hi", "hello", "avni", "tired", "sad", "happy", "fine", "bored", "good", "ok", "going"]
        
        # Safe check: Word count 3 se kam hona chahiye aur numeric nahi hona chahiye
        if extracted_name and len(extracted_name.split()) <= 3 and not extracted_name.isdigit():
            if not any(w == extracted_name.lower() for w in stop_words):
                profile["name"] = extracted_name.title()
                
    # 2. Age Extraction (Context safety filter check)
    age_match = re.search(r"(?:age|umar|saal|years?\s+old|i\s+am)\s*(\d{1,2})|(\d{1,2})\s*(?:saal|age|umar|years)", text)
    if age_match:
        age_str = age_match.group(1) or age_match.group(2)
        if age_str and not any(w in text for w in ["tired", "fine", "sad", "bored", "min"]):
            profile["age"] = int(age_str)

    return profile