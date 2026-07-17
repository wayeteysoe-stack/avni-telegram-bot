from core.extractors import extract_profile


def run():
    print("Testing extractors.py...")

    # Name Test
    profile = extract_profile("Mera naam Saurabh hai")
    assert profile["name"] == "Saurabh"

    # Age Test
    profile = extract_profile("Meri age 22 hai")
    assert profile["age"] == 22

    # Empty Test
    profile = extract_profile("Aaj mausam accha hai")
    assert profile == {}

    print("✅ extractors.py Passed")


if __name__ == "__main__":
    run()