# avni-bot/core/memory.py
from core.config import HISTORY_LIMIT

def get_profile(context):
    if "profile" not in context.user_data:
        context.user_data["profile"] = {}
    return context.user_data["profile"]

def update_profile(context, new_data: dict):
    profile = get_profile(context)
    for key, value in new_data.items():
        profile[key] = value
    context.user_data["profile"] = profile

def get_history(context):
    if "history" not in context.user_data:
        context.user_data["history"] = []
    return context.user_data["history"]

def add_history(context, role: str, text: str):
    """
    Saves message using strictly valid SDK roles ('user' or 'model').
    """
    history = get_history(context)
    # Mapping custom indicators to standard API roles
    api_role = "user" if role.lower() == "user" else "model"
    
    history.append({
        "role": api_role,
        "parts": [{"text": text}]
    })
    
    # Auto-trim history to optimize free-tier tokens
    context.user_data["history"] = history[-HISTORY_LIMIT:]

def build_profile_prompt(profile: dict) -> str:
    if not profile:
        return ""
    lines = ["[USER PROFILE MEMORY (Always Remember)]"]
    for key, value in profile.items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)