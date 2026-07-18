# avni-bot/core/storage.py
import os
import json
import logging

logger = logging.getLogger(__name__)

# Disk par data save karne ke liye data directory setup
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def get_user_file_path(user_id: int) -> str:
    """
    User ID ke basis par specific JSON file path return karta hai.
    """
    return os.path.join(DATA_DIR, f"user_{user_id}.json")

def save_user_state(user_id: int, context_data: dict) -> bool:
    """
    Telegram user_data state (history aur profile) ko disk par save karta hai.
    """
    if not user_id:
        return False
        
    file_path = get_user_file_path(user_id)
    try:
        # Extract only serializable pipeline data to avoid telegram object crashes
        serializable_data = {
            "profile": context_data.get("profile", {}),
            "history": context_data.get("history", [])
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=4)
        logger.info(f"[STORAGE WRITE SUCCESS]: State persistent for User ID {user_id}")
        return True
    except Exception as e:
        logger.error(f"[STORAGE WRITE ERROR]: Failed to save state for user {user_id}: {e}")
        return False

def load_user_state(user_id: int) -> dict:
    """
    Disk se user ka saved data read karke load karta hai.
    """
    file_path = get_user_file_path(user_id)
    if not os.path.exists(file_path):
        return {"profile": {}, "history": []}
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"[STORAGE READ SUCCESS]: Loaded state for User ID {user_id}")
        return data
    except Exception as e:
        logger.error(f"[STORAGE READ ERROR]: Failed to load state for user {user_id}: {e}")
        return {"profile": {}, "history": []}
