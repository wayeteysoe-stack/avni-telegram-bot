import logging
from typing import List, Dict, Any, Tuple
from storage.db import get_user_facts, get_recent_conversation
from core.prompt import SYSTEM_PROMPT
from core.behavior import analyze_behavior_context
from core.relationship import get_relationship_context
from core.response_style import get_style_controls
from google.genai import types

logger = logging.getLogger(__name__)

# Keywords that indicate contextual relevance for bringing up facts
RELEVANCE_KEYWORDS = {"yaad", "pata", "kaun", "kya", "batao", "favourite", "favorite", "like", "pasand", "birthday", "drink", "color"}

def _clean_text(raw_data: Any) -> str:
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

def build_full_prompt_context(telegram_id: int, current_user_text: str) -> Tuple[List[types.Content], str, str]:
    # 1. Fetch persistent user facts
    user_facts = get_user_facts(telegram_id, min_importance=50)
    fact_context_str = ""
    
    clean_text_lower = current_user_text.lower()
    
    # Topic Relevance Check: Inject facts ONLY if relevant keywords match
    is_relevant = any(kw in clean_text_lower for kw in RELEVANCE_KEYWORDS)
    if user_facts and is_relevant:
        facts_list = [f"- {key.replace('_', ' ').title()}: {val}" for key, val in user_facts.items()]
        fact_context_str = "\n\nREMEMBERED FACTS ABOUT USER (Use naturally ONLY if relevant to current conversation):\n" + "\n".join(facts_list)

    # 2. Fetch Recent History (Capped at 12)
    history_from_db = get_recent_conversation(telegram_id, limit=12)

    # 3. Behavior Analysis
    primary_mood, raw_mood = analyze_behavior_context(current_user_text, history_from_db)
    rel_context = get_relationship_context(interaction_count=len(history_from_db))
    style_controls = get_style_controls(primary_mood)

    # 4. Directive Composition
    context_directive = f"""

CURRENT CONVERSATION DIRECTIVE:
- Emotional Atmosphere: User sounds {primary_mood.lower()}.
- Direction: React naturally first. Keep tone spontaneous, avoid repeating phrases, and keep replies concise.
- Response Max Length: Max {style_controls['max_words']} words.
"""

    dynamic_system_instruction = SYSTEM_PROMPT + fact_context_str + context_directive

    contents: List[types.Content] = []
    clean_current = current_user_text.strip().lower()

    if history_from_db:
        for msg in history_from_db:
            if isinstance(msg, dict):
                role = "user" if msg.get("role") == "user" else "model"
                text = _clean_text(msg.get("parts", "")).strip()
                
                if role == "user" and text.lower() == clean_current:
                    continue
                    
                if text:
                    contents.append(
                        types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=text)]
                        )
                    )

    if current_user_text.strip():
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=current_user_text.strip())]
            )
        )

    return contents, dynamic_system_instruction, primary_mood