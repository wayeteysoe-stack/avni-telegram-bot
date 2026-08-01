import random
import re
import logging

logger = logging.getLogger(__name__)

VARIATION_OPENINGS = {
    "are_yaar": ["Arre yaar...", "Are yaar...", "Arey...", "Arre..."],
    "sach_me": ["Sach me?", "Seriously?", "Sach mein?", "Achaa?"],
    "oh_no": ["Oh no...", "Oho...", "Arre re..."],
}

def humanize_response(raw_text: str, mood: str = "CASUAL") -> str:
    """
    Post-processing layer to inject realistic human variations and strip remaining AI telltales.
    """
    if not raw_text:
        return raw_text

    text = raw_text.strip()

    # 1. Strip surrounding quotes
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1].strip()

    # 2. Randomize Common Hindi Openers
    if text.lower().startswith("are yaar") or text.lower().startswith("arre yaar"):
        replacement = random.choice(VARIATION_OPENINGS["are_yaar"])
        text = re.sub(r"^(?i)ar+e\s+yaar[\.,\s]*", f"{replacement} ", text)

    elif text.lower().startswith("sach me") or text.lower().startswith("seriously"):
        replacement = random.choice(VARIATION_OPENINGS["sach_me"])
        text = re.sub(r"^(?i)(sach\s+me|seriously)[\?\.,\s]*", f"{replacement} ", text)

    # 3. Random Lowercase First Word Injection
    words = text.split()
    if len(words) > 0 and random.random() < 0.35 and mood != "SERIOUS":
        words[0] = words[0].lower()
        text = " ".join(words)

    return text.strip()