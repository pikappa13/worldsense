from __future__ import annotations

from typing import Any

from worldsense.rules import keyword_matches, load_risk_rules
from worldsense.schemas import Consequence, ProbabilityLevel, RiskCategory, SeverityLevel, TimeHorizon


def _build_consequence(rule: dict[str, Any], description: str) -> Consequence:
    return Consequence(
        description=description,
        category=RiskCategory(rule["risk_category"]),
        probability=ProbabilityLevel(rule.get("probability", "medium")),
        severity=SeverityLevel(rule.get("severity", "medium")),
        time_horizon=TimeHorizon(rule.get("time_horizon", "unknown")),
        reversible=rule.get("reversible"),
        mitigation=rule.get("mitigation"),
    )


def generate_consequences(
    user_message: str,
    proposed_response: str | None = None,
) -> tuple[list[Consequence], list[dict[str, Any]]]:
    text = f"{user_message}\n{proposed_response or ''}"
    triggered: list[dict[str, Any]] = []
    consequences: list[Consequence] = []

    for rule in load_risk_rules():
        keyword_groups = rule.get("triggers", {}).get("keyword_groups", [])
        if any(keyword_matches(text, group) for group in keyword_groups):
            triggered.append(rule)
            consequences.extend(
                _build_consequence(rule, description)
                for description in rule.get("consequences", [])
            )

    return consequences, triggered

