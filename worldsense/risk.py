from __future__ import annotations

from worldsense.schemas import Consequence, ProbabilityLevel, RiskLevel, SeverityLevel


RISK_ORDER = {
    RiskLevel.NONE: 0,
    RiskLevel.LOW: 1,
    RiskLevel.MEDIUM: 2,
    RiskLevel.HIGH: 3,
    RiskLevel.CRITICAL: 4,
}

SEVERITY_WEIGHT = {
    SeverityLevel.LOW: 0.2,
    SeverityLevel.MEDIUM: 0.45,
    SeverityLevel.HIGH: 0.75,
    SeverityLevel.CRITICAL: 1.0,
}

PROBABILITY_WEIGHT = {
    ProbabilityLevel.UNKNOWN: 0.55,
    ProbabilityLevel.LOW: 0.25,
    ProbabilityLevel.MEDIUM: 0.6,
    ProbabilityLevel.HIGH: 0.9,
}


def max_risk(*levels: RiskLevel) -> RiskLevel:
    if not levels:
        return RiskLevel.NONE
    return max(levels, key=lambda level: RISK_ORDER[level])


def risk_score_for_consequence(consequence: Consequence) -> float:
    base = SEVERITY_WEIGHT[consequence.severity] * PROBABILITY_WEIGHT[consequence.probability]
    if consequence.reversible is False:
        base *= 1.25
    return min(base, 1.0)


def level_from_score(score: float) -> RiskLevel:
    if score >= 0.85:
        return RiskLevel.CRITICAL
    if score >= 0.6:
        return RiskLevel.HIGH
    if score >= 0.35:
        return RiskLevel.MEDIUM
    if score > 0:
        return RiskLevel.LOW
    return RiskLevel.NONE

