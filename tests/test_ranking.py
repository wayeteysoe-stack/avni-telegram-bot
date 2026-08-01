from memory.ranking import extract_ranked_facts

def run():
    print("Testing memory/ranking.py...")

    # 1. Birthday Test (Check: Duplicate facts na banein)
    facts = extract_ranked_facts("Mera birthday 14 March hai.")
    assert len(facts) == 1
    assert facts[0][0] == "birthday"
    assert facts[0][1] == "14 March"

    # 2. Preference Test (Check: 'bahut' word automatic remove ho)
    facts = extract_ranked_facts("Mujhe cold coffee bahut pasand hai.")
    assert len(facts) >= 1
    assert "cold coffee" in facts[0][1].lower()

    # 3. Question Filtering Test (Check: Sawaal 'kya hai' ko fact na samjhe)
    facts = extract_ranked_facts("Meri favourite drink kya hai?")
    assert len(facts) == 0  # Zero facts save hone chahiye

    print("✅ memory/ranking.py Passed Successfully!")

if __name__ == "__main__":
    run()