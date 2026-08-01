import logging
from typing import List, Dict, Any, Tuple
from storage.db import get_user_facts, get_recent_conversation
from core.prompt import SYSTEM_PROMPT
from google.genai import types

logger = logging.getLogger(__name__)

def _clean_text(raw_data: Any) -> str:
    """Helper to safely flatten text parts into a clean string."""
    if isinstance(raw_data, str):
        return raw_data
    if isinstance(raw_data, dict):
        if "text" in raw_data:
            return _clean_text(raw_data["text"])
        if "parts" in raw_data:
            return _clean_text(raw_data["parts"])
    if isinstance(raw_data, list):
        return " ".join([_clean_text(i) for i in raw_data if i])
    return str(raw_data) if raw_data is not None else ""

def build_full_prompt_context(telegram_id: int, current_user_text: str) -> Tuple[List[types.Content], str]:
    """
    Loads persistent facts & recent history from SQLite DB.
    Prevents duplication of the current user message in Gemini content context.
    """
    # 1. Fetch persistent user facts from SQLite DB
    user_facts = get_user_facts(telegram_id, min_importance=50)
    
    # 2. Build Memory Context Injection
    fact_context_str = ""
    if user_facts:
        facts_list = [f"- {key.replace('_', ' ').title()}: {val}" for key, val in user_facts.items()]
        fact_context_str = "\n\nREMEMBERED FACTS ABOUT USER:\n" + "\n".join(facts_list)

    dynamic_system_instruction = SYSTEM_PROMPT + fact_context_str

    # 3. Load recent conversation turns from SQLite DB
    history_from_db = get_recent_conversation(telegram_id, limit=20)

    contents: List[types.Content] = []
    clean_current = current_user_text.strip().lower()

    if history_from_db:
        for msg in history_from_db:
            if isinstance(msg, dict):
                role = "user" if msg.get("role") == "user" else "model"
                text = _clean_text(msg.get("parts", "")).strip()
                
                # Deduplication Guard: Ignore if history tail already contains current message
                if role == "user" and text.lower() == clean_current:
                    continue
                    
                if text:
                    contents.append(
                        types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=text)]
                        )
                    )

    # 4. Append current text cleanly at the end
    if current_user_text.strip():
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=current_user_text.strip())]
            )
        )

    logger.info("[CONTEXT BUILDER]: User %d -> Injected %d facts, %d history turns.", 
                telegram_id, len(user_facts), len(contents))

    return contents, dynamic_system_instruction