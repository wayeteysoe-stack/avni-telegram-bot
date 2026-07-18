# avni-bot/core/memory.py
from core.config import HISTORY_LIMIT

def get_profile(context) -> dict:
    if "profile" not in context.user_data:
        context.user_data["profile"] = {}
    return context.user_data["profile"]

def update_profile(context, new_data: dict) -> None:
    """
    User profile dictionary ko safely state context me merge karta hai.
    """
    profile = get_profile(context).copy()  # Safe shallow copy to avoid reference locks
    for key, value in new_data.items():
        if value:  # Only update if value is valid
            profile[key] = value
    context.user_data["profile"] = profile

def get_history(context) -> list:
    if "history" not in context.user_data:
        context.user_data["history"] = []
    return context.user_data["history"]

def add_history(context, role: str, text: str) -> None:
    """
    Saves message using strictly valid SDK roles ('user' or 'model').
    """
    history = get_history(context)
    
    # Mapping to strict SDK role specifications
    api_role = "user" if role.lower() == "user" else "model"
    
    history.append({
        "role": api_role,
        "parts": [{"text": text}]
    })
    
    # Auto-trim history structure using token layout threshold
    context.user_data["history"] = history[-HISTORY_LIMIT:]

def build_profile_prompt(profile: dict) -> str:
    if not profile:
        return ""
    lines = ["[USER PROFILE MEMORY (Always Remember)]"]
    for key, value in profile.items():
        if value:
            # Snake case key ko clean readable context label me badla (e.g., favorite_food -> Favorite Food)
            clean_key = key.replace("_", " ").title()
            lines.append(f"- {clean_key}: {value}")
    return "\n".join(lines)
