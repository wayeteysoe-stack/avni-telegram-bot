import re
import logging

logger = logging.getLogger(__name__)

def clean_ai_punctuation(text: str) -> str:
    """Strips unnatural AI punctuation like triple dots or excessive exclamations."""
    text = re.sub(r"\.{2,}", ".", text)
    text = re.sub(r"!{2,}", "!", text)
    text = re.sub(r"\?{2,}", "?", text)
    return text.strip()

def humanize_response(raw_text: str, mood: str = "CASUAL") -> str:
    """
    Focused Post-processor: Removes quotes, cleans punctuation, and preserves natural tone.
    """
    if not raw_text:
        return raw_text

    text = raw_text.strip()

    # 1. Strip surrounding quotation marks
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1].strip()

    # 2. Clean Excessive Punctuation
    text = clean_ai_punctuation(text)

    # 3. Strip robotic AI phrases
    robotic_phrases = ["as an ai", "i am an ai", "as a language model"]
    for phrase in robotic_phrases:
        if phrase in text.lower():
            text = re.sub(rf"(?i){phrase}", "", text).strip()

    return text.strip()