import sqlite3
import logging
from typing import List, Dict, Any
from storage.schema import DB_PATH, init_db

logger = logging.getLogger(__name__)

# Guarantee database structure initialization on module load
init_db()

FILLER_WORDS = {"ok", "okk", "hmm", "hmmm", "nhi", "haan", "acha", "achaa", "lol", "haha", "👍", "😂", "???", "123456"}

def _get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# ==================== USER OPERATIONS ====================

def ensure_user(telegram_id: int, first_name: str = ""):
    """Registers or updates user dynamically with actual Telegram name."""
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            if first_name and str(first_name).strip():
                cursor.execute(
                    """
                    INSERT INTO users (telegram_id, first_name) VALUES (?, ?)
                    ON CONFLICT(telegram_id) DO UPDATE SET first_name=excluded.first_name
                    """,
                    (telegram_id, str(first_name).strip())
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO users (telegram_id, first_name) VALUES (?, ?)
                    ON CONFLICT(telegram_id) DO NOTHING
                    """,
                    (telegram_id, "")
                )
            conn.commit()
    except Exception as e:
        logger.exception("[DB ERROR - ensure_user]: Failed to ensure user %s", telegram_id)

# ==================== FACTS & PROFILE OPERATIONS ====================

def save_fact(telegram_id: int, fact_key: str, fact_value: str, fact_type: str = "profile", importance: int = 50, first_name: str = ""):
    """Saves or updates a ranked memory fact for a user."""
    ensure_user(telegram_id, first_name=first_name)
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO facts (user_id, fact_key, fact_value, fact_type, importance, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id, fact_key) DO UPDATE SET
                    fact_value = excluded.fact_value,
                    fact_type = excluded.fact_type,
                    importance = excluded.importance,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (telegram_id, fact_key.strip().lower(), fact_value.strip(), fact_type, importance)
            )
            conn.commit()
            logger.info("[DB FACT SAVED]: User %s -> [%s] %s: %s (Score: %s)", telegram_id, fact_type, fact_key, fact_value, importance)
    except Exception as e:
        logger.exception("[DB ERROR - save_fact]: Failed to save fact for user %s", telegram_id)

def get_user_facts(telegram_id: int, min_importance: int = 0) -> Dict[str, str]:
    """Retrieves stored facts formatted for prompt context building."""
    facts = {}
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT fact_key, fact_value FROM facts WHERE user_id = ? AND importance >= ? ORDER BY importance DESC",
                (telegram_id, min_importance)
            )
            rows = cursor.fetchall()
            for r in rows:
                facts[r["fact_key"]] = r["fact_value"]
    except Exception as e:
        logger.exception("[DB ERROR - get_user_facts]: Failed to fetch facts for user %s", telegram_id)
    return facts

# ==================== CONVERSATION HISTORY ====================

def save_message(telegram_id: int, role: str, message: str, token_estimate: int = 0, first_name: str = ""):
    """Saves a single chat turn to persistent storage, filtering out low-value fillers."""
    if not message or not str(message).strip():
        return

    clean_msg = str(message).strip().lower()
    
    # Do not flood history DB with meaningless fillers
    if clean_msg in FILLER_WORDS or (len(clean_msg) <= 2 and not clean_msg.isalnum()):
        logger.info("[DB STORAGE]: Filtered filler message from history persistence: '%s'", message)
        return

    ensure_user(telegram_id, first_name=first_name)
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversation (user_id, role, message, token_estimate) VALUES (?, ?, ?, ?)",
                (telegram_id, role, str(message).strip(), token_estimate)
            )
            conn.commit()
    except Exception as e:
        logger.exception("[DB ERROR - save_message]: Failed to save message for user %s", telegram_id)

def get_recent_conversation(telegram_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieves the last N messages formatted for Gemini context."""
    history = []
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT role, message FROM (
                    SELECT id, role, message FROM conversation
                    WHERE user_id = ?
                    ORDER BY id DESC LIMIT ?
                ) ORDER BY id ASC
                """,
                (telegram_id, limit)
            )
            rows = cursor.fetchall()
            for r in rows:
                history.append({
                    "role": r["role"],
                    "parts": [r["message"]]
                })
    except Exception as e:
        logger.exception("[DB ERROR - get_recent_conversation]: Failed to fetch conversation for user %s", telegram_id)
    return history