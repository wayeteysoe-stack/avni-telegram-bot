# avni-bot/core/extractors.py
import re

def extract_profile(message: str) -> dict:
    """
    Strict regex aur context validation ke sath User Profile facts extract karta hai.
    """
    profile = {}
    msg = message.lower().strip()

    # 1. Age Extraction (First priority to resolve "I am [number]" clash)
    # Target: "meri age 22", "i am 22", "22 saal ka hu"
    age_match = re.search(r"(?:age|umar|saal|years?\s+old|i\s+am)\s*(\d{1,2})|(\d{1,2})\s*(?:saal|age|umar|years)", msg)
    extracted_age = None
    if age_match:
        age_str = age_match.group(1) or age_match.group(2)
        # Context safety filters
        if age_str and not any(w in msg for w in ["tired", "fine", "sad", "bored", "min", "ghanta"]):
            extracted_age = int(age_str)
            profile["age"] = extracted_age

    # 2. Name Extraction (Avoids digits/age conflict explicitly)
    # Target: "mera naam saurabh", "i am saurabh" (but NOT "i am 22")
    name_match = re.search(r"(?:mera\s+naam|my\s+name\s+is|i\s+am|i\'m)\s+([a-zA-Z\s]+?)(?:\s+hai|\.|$)", msg, re.IGNORECASE)
    if name_match:
        extracted_name = name_match.group(1).strip()
        stop_words = ["hi", "hello", "avni", "tired", "sad", "happy", "fine", "bored", "good", "ok", "going"]
        
        # Saraf wahi name valid hoga jo numeric na ho aur stop words me na ho
        if extracted_name and not extracted_name.isdigit() and not any(w == extracted_name for w in stop_words):
            # Safe check: agar pure message me koi age detect hui hai, toh use name me mat daalo
            if str(extracted_age) not in extracted_name:
                profile["name"] = extracted_name.title()

    # Context checklist for Preferences (Strict keyword + entity validation)
    has_pref_intent = any(word in msg for word in ["fav", "like", "love", "pasand", "achha", "best"])

    if has_pref_intent:
        # 3. Favorite Color Context Check
        color_list = ["blue", "red", "green", "black", "white", "yellow", "pink", "purple", "orange"]
        has_color_context = any(w in msg for w in ["color", "colour", "rang", "shade"])
        if has_color_context:
            for color in color_list:
                if re.search(rf"\b{color}\b", msg):
                    profile["favorite_color"] = color.title()
                    break

        # 4. Favorite Food Context Check
        food_list = ["pizza", "burger", "pasta", "biryani", "momo", "chole bhature", "maggi", "noodles", "samosa"]
        has_food_context = any(w in msg for w in ["food", "khana", "eat", "taste", "pasand", "favourite"])
        for food in food_list:
            if re.search(rf"\b{food}\b", msg):
                # Anti-repeat context filtering for things like "I love coding"
                if has_food_context or any(act in msg for act in ["khaya", "order", "swiggy", "zomato"]):
                    profile["favorite_food"] = food.title()
                    break

    return profile
