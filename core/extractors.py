# avni-bot/core/extractors.py
import re

def extract_profile(message: str) -> dict:
    """
    Strict word-count and context validation ke sath profile facts extract karta hai.
    """
    profile = {}
    msg = message.lower().strip()

    # 1. Age Extraction (First Priority)
    age_match = re.search(r"(?:age|umar|saal|years?\s+old|i\s+am)\s*(\d{1,2})|(\d{1,2})\s*(?:saal|age|umar|years)", msg)
    extracted_age = None
    if age_match:
        age_str = age_match.group(1) or age_match.group(2)
        if age_str and not any(w in msg for w in ["tired", "fine", "sad", "bored", "min", "ghanta"]):
            extracted_age = int(age_str)
            profile["age"] = extracted_age

    # 2. Name Extraction with strict Word Length & Intent Check
    name_match = re.search(r"(?:mera\s+naam|my\s+name\s+is|i\s+am|i\'m)\s+([a-zA-Z\s]+?)(?:\s+hai|\.|$)", msg, re.IGNORECASE)
    if name_match:
        extracted_name = name_match.group(1).strip()
        stop_words = ["hi", "hello", "avni", "tired", "sad", "happy", "fine", "bored", "good", "ok", "going", "going to"]
        
        # Validation: Word count 3 se kam hona chahiye aur numeric nahi hona chahiye
        if extracted_name and len(extracted_name.split()) <= 3 and not extracted_name.isdigit():
            if not any(w in extracted_name.lower() for w in stop_words):
                if str(extracted_age) not in extracted_name:
                    profile["name"] = extracted_name.title()

    # Preferences checking logic
    has_pref_intent = any(word in msg for word in ["fav", "like", "love", "pasand", "achha", "best"])
    if has_pref_intent:
        color_list = ["blue", "red", "green", "black", "white", "yellow", "pink", "purple", "orange"]
        if any(w in msg for w in ["color", "colour", "rang", "shade"]):
            for color in color_list:
                if re.search(rf"\b{color}\b", msg):
                    profile["favorite_color"] = color.title()
                    break

        food_list = ["pizza", "burger", "pasta", "biryani", "momo", "chole bhature", "maggi", "noodles", "samosa"]
        has_food_context = any(w in msg for w in ["food", "khana", "eat", "taste", "pasand", "favourite"])
        for food in food_list:
            if re.search(rf"\b{food}\b", msg):
                if has_food_context or any(act in msg for act in ["khaya", "order", "swiggy", "zomato"]):
                    profile["favorite_food"] = food.title()
                    break

    return profile