from typing import List, Dict, Any
from google.genai import types

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

def build_gemini_contents(user_text: str, conversation_history: List[Dict[str, Any]] = None) -> List[types.Content]:
    contents: List[types.Content] = []

    if conversation_history:
        for msg in conversation_history:
            if isinstance(msg, dict):
                role = "user" if msg.get("role") == "user" else "model"
                text = _clean_text(msg.get("parts", "")).strip()
                if text:
                    contents.append(
                        types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=text)]
                        )
                    )

    if str(user_text).strip():
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=str(user_text).strip())]
            )
        )

    return contents