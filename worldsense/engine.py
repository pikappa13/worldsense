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
    Consequence,
    ImplicitContext,
    ProbabilityLevel,
    Recommendation,
    RealityAnalysis,
    RewriteGuidance,
    RiskAssessment,
    RiskCategory,
    RiskLevel,
    SeverityLevel,
    TimeHorizon,
)
from worldsense.social import assess_social_context
from worldsense.uncertainty import detect_uncertainty


class RealityEngine:
    """Reality-check engine for LLM responses and agent actions.

    Pass an optional ``adapter`` to enable LLM-assisted analysis on top of
    the rule-based core. Without an adapter the engine works fully offline.

    Example (Claude)::

        import anthropic
        from worldsense import RealityEngine
        from worldsense.adapters.claude_adapter import ClaudeAdapter

        engine = RealityEngine(adapter=ClaudeAdapter(anthropic.Anthropic()))

    Example (OpenAI)::

        import openai
        from worldsense import RealityEngine
        from worldsense.adapters.openai_adapter import OpenAIAdapter

        engine = RealityEngine(adapter=OpenAIAdapter(openai.OpenAI()))
    """

    def __init__(self, adapter: Any | None = None) -> None:
        self._adapter = adapter

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(
        self,
        user_message: str,
        proposed_response: str | None = None,
        context: dict[str, Any] | None = None,
        planned_action: dict[str, Any] | None = None,
    ) -> RealityAnalysis:
        context = context or {}
        intent = parse_intent(user_message)

        if self._adapter is not None:
            implicit_context = self._llm_extract_context(user_message, proposed_response)
        else:
            implicit_context = extract_implicit_context(user_message, proposed_response)

        world_state = build_world_state(user_message, implicit_context)
        consequences, triggered_rules = generate_consequences(user_message, proposed_response)

        if self._adapter is not None:
            llm_consequences = self._llm_simulate_consequences(user_message, proposed_response)
            existing_descs = {c.description for c in consequences}
            for c in llm_consequences:
                if c.description not in existing_descs:
                    consequences.append(c)

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
        if action_assessment:
            categories.extend(action_assessment.categories)
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

        if self._adapter is not None:
            rewrite_guidance = self._llm_rewrite_guidance(user_message, proposed_response, risk_level)
        else:
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

    # ------------------------------------------------------------------
    # LLM-assisted helpers (only called when self._adapter is set)
    # ------------------------------------------------------------------

    def _llm_extract_context(
        self, user_message: str, proposed_response: str | None
    ) -> ImplicitContext:
        from worldsense.adapters.base import LLMMessage
        from worldsense.prompts import ANALYZE_IMPLICIT_CONTEXT_PROMPT

        user_content = f"User message: {user_message}"
        if proposed_response:
            user_content += f"\n\nProposed response: {proposed_response}"

        try:
            data = self._adapter.complete_json([
                LLMMessage(role="system", content=ANALYZE_IMPLICIT_CONTEXT_PROMPT),
                LLMMessage(role="user", content=user_content),
            ])
            return ImplicitContext(
                signals=data.get("signals", []),
                constraints=data.get("constraints", []),
                assumptions=data.get("assumptions", []),
                missing_information=data.get("missing_information", []),
            )
        except Exception:  # noqa: BLE001
            return extract_implicit_context(user_message, proposed_response)

    def _llm_simulate_consequences(
        self, user_message: str, proposed_response: str | None
    ) -> list[Consequence]:
        from worldsense.adapters.base import LLMMessage
        from worldsense.prompts import SIMULATE_CONSEQUENCES_PROMPT

        user_content = f"User message: {user_message}"
        if proposed_response:
            user_content += f"\n\nProposed response: {proposed_response}"

        try:
            data = self._adapter.complete_json([
                LLMMessage(role="system", content=SIMULATE_CONSEQUENCES_PROMPT),
                LLMMessage(role="user", content=user_content),
            ])
            results: list[Consequence] = []
            for item in data.get("consequences", []):
                try:
                    results.append(Consequence(
                        description=item["description"],
                        category=RiskCategory(item.get("category", "operational")),
                        probability=ProbabilityLevel(item.get("probability", "unknown")),
                        severity=SeverityLevel(item.get("severity", "medium")),
                        time_horizon=TimeHorizon(item.get("time_horizon", "unknown")),
                        reversible=item.get("reversible"),
                        mitigation=item.get("mitigation"),
                    ))
                except (KeyError, ValueError):
                    continue
            return results
        except Exception:  # noqa: BLE001
            return []

    def _llm_rewrite_guidance(
        self,
        user_message: str,
        proposed_response: str | None,
        risk_level: RiskLevel,
    ) -> RewriteGuidance:
        from worldsense.adapters.base import LLMMessage
        from worldsense.prompts import REWRITE_RESPONSE_PROMPT

        if risk_level in (RiskLevel.NONE, RiskLevel.LOW):
            return build_rewrite_guidance(risk_level, [])

        user_content = (
            f"User message: {user_message}\n"
            f"Risk level: {risk_level}\n"
        )
        if proposed_response:
            user_content += f"\nProposed response: {proposed_response}"

        try:
            data = self._adapter.complete_json([
                LLMMessage(role="system", content=REWRITE_RESPONSE_PROMPT),
                LLMMessage(role="user", content=user_content),
            ])
            return RewriteGuidance(
                rewrite_strategy=data.get("rewrite_strategy"),
                must_include=data.get("must_include", []),
                avoid=data.get("avoid", []),
                tone=data.get("tone"),
            )
        except Exception:  # noqa: BLE001
            return build_rewrite_guidance(risk_level, [])

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

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
