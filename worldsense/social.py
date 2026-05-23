from __future__ import annotations

from worldsense.schemas import RiskLevel, SocialAssessment


def assess_social_context(user_message: str, proposed_response: str | None = None) -> SocialAssessment:
    text = f"{user_message}\n{proposed_response or ''}".casefold()
    if any(word in text for word in ["capo", "manager", "cliente", "boss"]):
        return SocialAssessment(
            social_risk=RiskLevel.MEDIUM,
            likely_reactions=[
                "The recipient may interpret defensive or emotional wording negatively.",
                "A poor tone could increase reputation or workplace friction.",
            ],
            tone_recommendation="neutral, specific, professional",
            escalation_risk=RiskLevel.MEDIUM,
            safer_framing="Acknowledge the issue, state facts briefly, and propose a next step.",
        )
    return SocialAssessment()

