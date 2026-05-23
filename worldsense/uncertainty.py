from __future__ import annotations

from worldsense.schemas import UncertaintyAssessment


TIME_SENSITIVE_TERMS = [
    "latest",
    "today",
    "current",
    "most recent",
    "oggi",
    "attuale",
    "piu recente",
    "più recente",
]


def detect_uncertainty(
    user_message: str,
    proposed_response: str | None = None,
    missing_context: list[str] | None = None,
) -> UncertaintyAssessment:
    text = f"{user_message}\n{proposed_response or ''}".casefold()
    missing = list(missing_context or [])
    assumptions: list[str] = []
    unsupported_claims: list[str] = []

    if any(term in text for term in ["miglior", "best", "cheapest", "piu economico"]):
        assumptions.append("The user's ranking criteria may be underspecified.")
        if "decision_criteria" not in missing:
            missing.append("decision_criteria")

    if proposed_response and any(term in proposed_response.casefold() for term in TIME_SENSITIVE_TERMS):
        unsupported_claims.append("The response may contain time-sensitive claims that need verification.")

    if any(term in text for term in ["sicuramente", "definitely", "certainly", "garantito"]):
        unsupported_claims.append("The wording signals confidence that may not be supported by context.")

    should_search = bool(unsupported_claims and any(term in text for term in TIME_SENSITIVE_TERMS))
    should_ask = bool(missing)
    should_refuse = bool(unsupported_claims and not proposed_response)
    confidence = 0.8
    if missing:
        confidence -= 0.2
    if unsupported_claims:
        confidence -= 0.25

    return UncertaintyAssessment(
        assumptions=sorted(set(assumptions)),
        unsupported_claims=sorted(set(unsupported_claims)),
        missing_context=sorted(set(missing)),
        confidence=max(confidence, 0.1),
        should_ask_user=should_ask,
        should_search_external_sources=should_search,
        should_refuse_to_guess=should_refuse,
    )

