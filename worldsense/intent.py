from __future__ import annotations

from worldsense.schemas import IntentAnalysis, RiskLevel


INTENT_KEYWORDS = {
    "drive_while_tired": ["guidare", "stanco"],
    "delete_files": ["cancella", "file"],
    "reply_to_boss": ["rispondere", "capo"],
    "resign_impulsively": ["licenziarmi", "oggi"],
    "food_safety": ["cibo", "fuori"],
    "expensive_purchase": ["comprare", "costoso"],
    "impossible_trip": ["un giorno", "venezia", "milano"],
    "privacy_sensitive_request": ["documento", "invia"],
}


def parse_intent(user_message: str) -> IntentAnalysis:
    normalized = user_message.casefold()
    matches = [
        intent
        for intent, keywords in INTENT_KEYWORDS.items()
        if all(keyword in normalized for keyword in keywords)
    ]

    if not matches:
        return IntentAnalysis(primary_intent="unknown", confidence=0.25, ambiguity_level=RiskLevel.MEDIUM)

    return IntentAnalysis(
        primary_intent=matches[0],
        secondary_intents=matches[1:],
        confidence=0.75 if len(matches) == 1 else 0.6,
        ambiguity_level=RiskLevel.LOW if len(matches) == 1 else RiskLevel.MEDIUM,
    )
