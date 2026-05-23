from __future__ import annotations

from typing import Any

from worldsense.actions import evaluate_action as evaluate_agent_action
from worldsense.consequences import generate_consequences
from worldsense.constraints import detect_constraint_violations
from worldsense.context import build_world_state, extract_implicit_context
from worldsense.intent import parse_intent
from worldsense.rewrite import build_rewrite_guidance
from worldsense.risk import level_from_score, max_risk, risk_score_for_consequence
from worldsense.schemas import (
    ActionAssessment,
    Recommendation,
    RealityAnalysis,
    RiskAssessment,
    RiskCategory,
    RiskLevel,
)
from worldsense.social import assess_social_context
from worldsense.uncertainty import detect_uncertainty


class RealityEngine:
    """Rule-based reality-check engine for LLM responses and agent actions."""

    def analyze(
        self,
        user_message: str,
        proposed_response: str | None = None,
        context: dict[str, Any] | None = None,
        planned_action: dict[str, Any] | None = None,
    ) -> RealityAnalysis:
        context = context or {}
        intent = parse_intent(user_message)
        implicit_context = extract_implicit_context(user_message, proposed_response)
        world_state = build_world_state(user_message, implicit_context)
        consequences, triggered_rules = generate_consequences(user_message, proposed_response)
        constraint_violations = detect_constraint_violations(user_message, proposed_response)
        uncertainty_assessment = detect_uncertainty(
            user_message,
            proposed_response,
            implicit_context.missing_information,
        )
        action_assessment = (
            evaluate_agent_action(planned_action, context) if planned_action is not None else None
        )

        score = max((risk_score_for_consequence(item) for item in consequences), default=0.0)
        consequence_level = level_from_score(score)
        rule_levels = [RiskLevel(rule.get("min_risk_level", "none")) for rule in triggered_rules]
        action_level = action_assessment.risk_level if action_assessment else RiskLevel.NONE
        constraint_level = max_risk(
            *(violation.severity for violation in constraint_violations)
        )
        risk_level = max_risk(consequence_level, action_level, constraint_level, *rule_levels)

        categories = sorted(
            {item.category for item in consequences}
            | {
                RiskCategory(rule["risk_category"])
                for rule in triggered_rules
                if rule.get("risk_category")
            },
            key=lambda category: category.value,
        )

        if implicit_context.missing_information:
            categories.append(RiskCategory.MISSING_CONTEXT)
        if constraint_violations:
            categories.extend(
                RiskCategory.TRAVEL_LOGISTICS
                for item in constraint_violations
                if item.constraint_type == "travel_logistics"
            )
            categories.extend(
                RiskCategory.OPERATIONAL
                for item in constraint_violations
                if item.constraint_type == "operational_safety"
            )

        risk = RiskAssessment(
            risk_level=risk_level,
            risk_score=score,
            categories=sorted(set(categories), key=lambda category: category.value),
            reasons=[
                rule.get("recommendation", rule["id"])
                for rule in triggered_rules
                if rule.get("recommendation") or rule.get("id")
            ]
            + [item.description for item in constraint_violations],
            uncertainty=RiskLevel.MEDIUM if implicit_context.missing_information else RiskLevel.LOW,
        )

        recommendations = self._build_recommendations(triggered_rules, action_assessment, risk_level)
        social_assessment = assess_social_context(user_message, proposed_response)
        rewrite_guidance = build_rewrite_guidance(risk_level, consequences)

        return RealityAnalysis(
            intent=intent,
            implicit_context=implicit_context,
            world_state=world_state,
            consequences=consequences,
            risk=risk,
            recommendations=recommendations,
            action_assessment=action_assessment,
            social_assessment=social_assessment,
            constraint_violations=constraint_violations,
            uncertainty_assessment=uncertainty_assessment,
            rewrite_guidance=rewrite_guidance,
            triggered_rules=[rule["id"] for rule in triggered_rules],
        )

    def check_response(self, user_message: str, proposed_response: str) -> RealityAnalysis:
        return self.analyze(user_message=user_message, proposed_response=proposed_response)

    def evaluate_action(
        self,
        action: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> ActionAssessment:
        return evaluate_agent_action(action, context)

    def _build_recommendations(
        self,
        triggered_rules: list[dict[str, Any]],
        action_assessment: ActionAssessment | None,
        risk_level: RiskLevel,
    ) -> list[Recommendation]:
        recommendations = [
            Recommendation(
                action=rule.get("recommended_action", "review_before_answering"),
                rationale=rule.get("recommendation", rule["id"]),
                priority=RiskLevel(rule.get("min_risk_level", risk_level.value)),
            )
            for rule in triggered_rules
        ]

        if action_assessment and action_assessment.requires_confirmation:
            recommendations.append(
                Recommendation(
                    action="require_confirmation",
                    rationale="The planned action has side effects or missing required context.",
                    priority=action_assessment.risk_level,
                )
            )

        if not recommendations and risk_level is RiskLevel.NONE:
            recommendations.append(
                Recommendation(
                    action="proceed",
                    rationale="No configured rule identified a material real-world risk.",
                    priority=RiskLevel.LOW,
                )
            )

        return recommendations
