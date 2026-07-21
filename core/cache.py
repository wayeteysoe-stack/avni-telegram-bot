# avni-bot/core/cache.py
import random

CACHE_REPLIES = {
    "hi": ["Hii", "Heyy", "Haan bolo"],
    "hii": ["Hii", "Hey", "Haanji"],
    "hello": ["Hello", "Hey", "Haanji bolo"],
    "hey": ["Heyy", "Hii", "Haan bolo"],

    "ok": ["Achaa", "Okk", "Hmm"],
    "okay": ["Achaa okk", "Hmm thik hai"],

    "thanks": ["Arey koi na", "Mention not yaar", "Welcome"],
    "thank you": ["Koi na yaar", "Welcome"],

    "bye": ["Bye", "Chalo bye", "Take care"],

    "good night": ["Good night", "Gn! Kal baat karte hain"],
    "good morning": ["Good morning", "Gm!"],

    "hmm": ["Hmm", "Aage bolo", "Kahan khoye ho?"],
}

def get_cached_reply(message: str):
    """
    Agar message cache me hai to natural random reply return karega.
    """
    msg = message.lower().strip()
    if msg in CACHE_REPLIES:
        return random.choice(CACHE_REPLIES[msg])
    return None