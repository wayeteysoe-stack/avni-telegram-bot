from core.cache import get_cached_reply

def run():
    print("Testing cache.py...")

    assert get_cached_reply("hi") in ["Hii", "Heyy", "Haan bolo"]
    assert get_cached_reply("hello") in ["Hello", "Hey", "Haanji bolo"]
    assert get_cached_reply("unknown_message_123") is None

    print("✅ cache.py Passed")

if __name__ == "__main__":
    run()