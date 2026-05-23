from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class RiskLevel(StrEnum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProbabilityLevel(StrEnum):
    UNKNOWN = "unknown"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SeverityLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TimeHorizon(StrEnum):
    IMMEDIATE = "immediate"
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"
    UNKNOWN = "unknown"


class RiskCategory(StrEnum):
    PHYSICAL_SAFETY = "physical_safety"
    MEDICAL = "medical"
    MENTAL_HEALTH = "mental_health"
    LEGAL = "legal"
    FINANCIAL = "financial"
    PRIVACY = "privacy"
    CYBERSECURITY = "cybersecurity"
    DATA_LOSS = "data_loss"
    REPUTATION = "reputation"
    SOCIAL_CONFLICT = "social_conflict"
    WORKPLACE = "workplace"
    RELATIONSHIP = "relationship"
    TRAVEL_LOGISTICS = "travel_logistics"
    OPERATIONAL = "operational"
    IRREVERSIBLE_ACTION = "irreversible_action"
    PUBLIC_COMMUNICATION = "public_communication"
    CHILD_SAFETY = "child_safety"
    THIRD_PARTY_HARM = "third_party_harm"
    MISINFORMATION = "misinformation"
    OVERCONFIDENCE = "overconfidence"
    MISSING_CONTEXT = "missing_context"


class IntentAnalysis(BaseModel):
    primary_intent: str = "unknown"
    secondary_intents: list[str] = Field(default_factory=list)
    hidden_intents: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    ambiguity_level: RiskLevel = RiskLevel.LOW


class ImplicitContext(BaseModel):
    signals: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)


class WorldState(BaseModel):
    actors: list[dict[str, Any]] = Field(default_factory=list)
    objects: list[dict[str, Any]] = Field(default_factory=list)
    constraints: list[dict[str, Any]] = Field(default_factory=list)
    current_state: str = "unknown"
    uncertainties: list[str] = Field(default_factory=list)


class Consequence(BaseModel):
    description: str
    category: RiskCategory
    probability: ProbabilityLevel = ProbabilityLevel.UNKNOWN
    severity: SeverityLevel = SeverityLevel.MEDIUM
    time_horizon: TimeHorizon = TimeHorizon.UNKNOWN
    reversible: bool | None = None
    mitigation: str | None = None


class Recommendation(BaseModel):
    action: str
    rationale: str
    priority: RiskLevel = RiskLevel.MEDIUM


class RiskAssessment(BaseModel):
    risk_level: RiskLevel = RiskLevel.NONE
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    categories: list[RiskCategory] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    uncertainty: RiskLevel = RiskLevel.LOW


class ActionAssessment(BaseModel):
    action_type: str
    risk_level: RiskLevel = RiskLevel.NONE
    categories: list[RiskCategory] = Field(default_factory=list)
    side_effect_type: str = "unknown"
    reversible: bool | None = None
    allow: bool = True
    should_warn: bool = False
    requires_confirmation: bool = False
    should_block: bool = False
    required_context: list[str] = Field(default_factory=list)
    recommended_confirmation_prompt: str | None = None
    safer_alternative: str | None = None
    reasons: list[str] = Field(default_factory=list)


class SocialAssessment(BaseModel):
    social_risk: RiskLevel = RiskLevel.NONE
    likely_reactions: list[str] = Field(default_factory=list)
    tone_recommendation: str | None = None
    escalation_risk: RiskLevel = RiskLevel.NONE
    safer_framing: str | None = None


class ConstraintViolation(BaseModel):
    constraint_type: str
    description: str
    severity: RiskLevel = RiskLevel.MEDIUM
    evidence: list[str] = Field(default_factory=list)
    mitigation: str | None = None


class UncertaintyAssessment(BaseModel):
    assumptions: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    missing_context: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    should_ask_user: bool = False
    should_search_external_sources: bool = False
    should_refuse_to_guess: bool = False


class RewriteGuidance(BaseModel):
    rewrite_strategy: str | None = None
    must_include: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)
    tone: str | None = None


class RealityAnalysis(BaseModel):
    intent: IntentAnalysis
    implicit_context: ImplicitContext
    world_state: WorldState
    consequences: list[Consequence] = Field(default_factory=list)
    risk: RiskAssessment
    recommendations: list[Recommendation] = Field(default_factory=list)
    action_assessment: ActionAssessment | None = None
    social_assessment: SocialAssessment | None = None
    constraint_violations: list[ConstraintViolation] = Field(default_factory=list)
    uncertainty_assessment: UncertaintyAssessment | None = None
    rewrite_guidance: RewriteGuidance | None = None
    triggered_rules: list[str] = Field(default_factory=list)


class ScenarioEvaluation(BaseModel):
    scenario_id: str
    passed: bool
    risk_met: bool
    categories_met: bool
    missing_context_met: bool
    expected_risk_level: RiskLevel
    actual_risk_level: RiskLevel
    expected_categories: list[RiskCategory] = Field(default_factory=list)
    actual_categories: list[RiskCategory] = Field(default_factory=list)
    expected_missing_context: list[str] = Field(default_factory=list)
    actual_missing_context: list[str] = Field(default_factory=list)
    expected_action: str | None = None
    actual_actions: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class BenchmarkReport(BaseModel):
    total: int
    passed: int
    failed: int
    pass_rate: float
    results: list[ScenarioEvaluation]


class ValidationIssue(BaseModel):
    source: str
    item_id: str | None = None
    message: str
    severity: RiskLevel = RiskLevel.HIGH


class ValidationReport(BaseModel):
    passed: bool
    checked_files: list[str] = Field(default_factory=list)
    issues: list[ValidationIssue] = Field(default_factory=list)
