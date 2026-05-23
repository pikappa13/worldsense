from __future__ import annotations

import re

from worldsense.schemas import ConstraintViolation, RiskLevel


def detect_constraint_violations(
    user_message: str,
    proposed_response: str | None = None,
) -> list[ConstraintViolation]:
    text = f"{user_message}\n{proposed_response or ''}".casefold()
    violations: list[ConstraintViolation] = []

    city_count = _extract_city_count(text)
    one_day = any(term in text for term in ["un giorno", "1 giorno", "one day", "single day"])
    if city_count and city_count >= 4 and one_day:
        violations.append(
            ConstraintViolation(
                constraint_type="travel_logistics",
                description="The plan appears to include too many cities for a single day.",
                severity=RiskLevel.HIGH,
                evidence=[f"city_count={city_count}", "time_window=one_day"],
                mitigation="Reduce the number of destinations or extend the schedule.",
            )
        )

    if any(term in text for term in ["senza budget", "no budget", "miglior hotel", "best hotel"]):
        violations.append(
            ConstraintViolation(
                constraint_type="economic_preference",
                description="The recommendation depends on budget and preference constraints that are missing.",
                severity=RiskLevel.MEDIUM,
                evidence=["budget_or_preference_missing"],
                mitigation="Ask for budget, dates, location, and decision criteria before choosing.",
            )
        )

    if any(term in text for term in ["rm -rf /", "format c:", "del /s c:\\"]):
        violations.append(
            ConstraintViolation(
                constraint_type="operational_safety",
                description="The command targets a broad or system-critical path.",
                severity=RiskLevel.CRITICAL,
                evidence=["broad_destructive_command"],
                mitigation="Block execution and require an explicit reviewed target.",
            )
        )

    return violations


def _extract_city_count(text: str) -> int | None:
    explicit = re.search(r"\b([4-9]|1[0-9])\s+(citta|città|cities)\b", text)
    if explicit:
        return int(explicit.group(1))

    known_city_mentions = [
        "roma",
        "milano",
        "venezia",
        "firenze",
        "napoli",
        "parigi",
        "londra",
        "berlino",
        "madrid",
        "barcellona",
    ]
    count = sum(1 for city in known_city_mentions if city in text)
    return count or None

