from __future__ import annotations

from worldsense.schemas import Consequence, RewriteGuidance, RiskCategory, RiskLevel


def build_rewrite_guidance(
    risk_level: RiskLevel,
    consequences: list[Consequence],
) -> RewriteGuidance | None:
    categories = {consequence.category for consequence in consequences}

    if risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
        guidance = RewriteGuidance(
            rewrite_strategy="increase_safety_and_practicality",
            tone="firm, calm, non-alarmist",
            avoid=["normalizing risky behavior", "overconfident advice without context"],
        )
        if RiskCategory.PHYSICAL_SAFETY in categories:
            guidance.must_include.extend(
                [
                    "state the safety risk plainly",
                    "suggest delaying the action or using a safer alternative",
                ]
            )
        if RiskCategory.DATA_LOSS in categories:
            guidance.must_include.extend(
                [
                    "verify the exact target before destructive operations",
                    "suggest backup or dry-run before proceeding",
                ]
            )
        return guidance

    if RiskCategory.MISSING_CONTEXT in categories:
        return RewriteGuidance(
            rewrite_strategy="ask_targeted_clarifying_questions",
            must_include=["ask only for information needed to make the decision safer"],
            avoid=["guessing user preferences"],
            tone="concise and helpful",
        )

    return None

