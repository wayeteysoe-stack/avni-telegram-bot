import random

CACHE_REPLIES = {
    "hi": ["Hii 😄", "Hey 😊", "Hii"],
    "hii": ["Hii 😄", "Heyy"],
    "hello": ["Hello 😊", "Hey 😄"],
    "hey": ["Hey 👋", "Hii"],

    "ok": ["Okk 👍", "Achaa 😄"],
    "okay": ["Okk 😊"],

    "thanks": ["Anytime 😄", "Welcome 😊"],
    "thank you": ["Welcome 😊", "Koi baat nhi 😄"],

    "bye": ["Bye 👋", "Take care 😊"],

    "good night": ["Good night 🌙", "Sweet dreams 😴"],
    "good morning": ["Good morning ☀️"],

    "hmm": ["Hmm 🤔", "Haan bolo"],

    "test123": ["CACHE WORKING ✅"],
}


def get_cached_reply(message: str):
    """
    Agar message cache me hai to
    random reply return karega.
    Nahi hai to None return karega.
    """

    message = message.lower().strip()

    if message in CACHE_REPLIES:
        return random.choice(CACHE_REPLIES[message])

    return None