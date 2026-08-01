from core.cache import get_cached_reply

def run():
    print("Testing cache.py...")

    assert get_cached_reply("hi") is not None
    assert get_cached_reply("hello") is not None
    assert get_cached_reply("unknown_message") is None

    print("✅ cache.py Passed")

if __name__ == "__main__":
    run()