import re
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

EMOTION_WEIGHTS = {
    "SUPPORTIVE": [
        (r"\b(?:sad|upset|depressed|hurt|pareshan|trouble|worried|crying|pain)\b", 3),
        (r"\b(?:job|office|boss|fired|loss|death|accident|sick|ill|hospital)\b", 2),
        (r"\b(?:mood\s+off|thak|stress|tension|ruined|bad\s+day)\b", 3)
    ],
    "EXCITED": [
        (r"\b(?:selected|promoted|passed|won|victory|party|celebrate|hurray|yay|wohoo)\b", 3),
        (r"\b(?:good\s+news|great\s+day|awesome|amazing|happy|excited)\b", 2)
    ],
    "PLAYFUL": [
        (r"\b(?:game|match|win|lost|hara|jeet|cheating|masti|funny|joke|prank)\b", 2),
        (r"\b(?:lol|lmao|haha|hehe|rofl)\b", 1)
    ],
    "RESPECTFUL_PROFESSIONAL": [
        (r"\b(?:cyber|security|coding|python|project|developer|engineer|client)\b", 2),
        (r"\b(?:meeting|presentation|work|office|deadline)\b", 2)
    ]
}

def analyze_behavior_context(user_text: str, history: List[Dict[str, Any]] = None) -> Tuple[str, str]:
    clean_text = user_text.lower().strip()
    scores = {mood: 0 for mood in EMOTION_WEIGHTS.keys()}

    for mood, patterns in EMOTION_WEIGHTS.items():
        for pattern, weight in patterns:
            if re.search(pattern, clean_text):
                scores[mood] += weight

    if history and len(clean_text.split()) <= 2:
        last_user_msgs = [m.get("parts", [""])[0] for m in history if m.get("role") == "user"]
        if last_user_msgs:
            recent_text = " ".join(last_user_msgs[-2:]).lower()
            for mood, patterns in EMOTION_WEIGHTS.items():
                for pattern, weight in patterns:
                    if re.search(pattern, recent_text):
                        scores[mood] += (weight // 2)

    sorted_moods = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_mood, top_score = sorted_moods[0]

    primary = top_mood if top_score > 0 else "FRIENDLY_CASUAL"
    return primary, top_mood