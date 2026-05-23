from __future__ import annotations

from typing import Any

from worldsense.rules import load_action_rules
from worldsense.schemas import ActionAssessment, RiskCategory, RiskLevel


def _value_is_present(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return value not in (None, "", [], {})


def _context_has(context: dict[str, Any], key: str) -> bool:
    value = context.get(key)
    return _value_is_present(value)


def _requirement_is_met(action: dict[str, Any], context: dict[str, Any], key: str) -> bool:
    if _context_has(context, key):
        return True
    if key == "exact_target":
        return _value_is_present(action.get("target"))
    if key == "recipient":
        return _value_is_present(action.get("recipient"))
    if key == "budget":
        return _value_is_present(action.get("budget"))
    return False


def evaluate_action(action: dict[str, Any], context: dict[str, Any] | None = None) -> ActionAssessment:
    context = context or {}
    action_type = str(action.get("type") or action.get("tool") or "unknown")
    target = str(action.get("target") or "")
    description = str(action.get("description") or "")
    action_text = f"{action_type} {target} {description}".casefold()

    matched_rule = None
    matched_by_type = False

    for rule in load_action_rules():
        rule_type = str(rule.get("action_type", "")).casefold()
        keywords = [str(keyword).casefold() for keyword in rule.get("keywords", [])]
        type_matches = rule_type and rule_type in action_type.casefold()
        keyword_matches = keywords and any(keyword in action_text for keyword in keywords)
        match_mode = rule.get("match_mode", "type_or_keyword")

        if match_mode == "type_and_keyword" and type_matches and keyword_matches:
            matched_rule = rule
            matched_by_type = True
            break
        if match_mode == "type_and_keyword":
            continue
        if type_matches:
            matched_rule = rule
            matched_by_type = True
            break
        if keyword_matches and matched_rule is None:
            matched_rule = rule

    if matched_rule is None:
        return ActionAssessment(action_type=action_type)

    required_context = [
        key
        for key in matched_rule.get("requires_context", [])
        if not _requirement_is_met(action, context, key)
    ]
    requires_confirmation = bool(matched_rule.get("requires_confirmation", False))
    should_block = bool(matched_rule.get("block_without_required_context", False) and required_context)

    reasons = list(matched_rule.get("reasons", []))
    if not matched_by_type:
        reasons.append("Matched by keyword because no more specific action type rule matched.")
    categories = [
        RiskCategory(category)
        for category in matched_rule.get("risk_categories", matched_rule.get("categories", []))
    ]
    if not categories and matched_rule.get("risk_category"):
        categories = [RiskCategory(matched_rule["risk_category"])]

    return ActionAssessment(
        action_type=action_type,
        risk_level=RiskLevel(matched_rule.get("risk_level", "medium")),
        categories=categories,
        side_effect_type=matched_rule.get("side_effect_type", "unknown"),
        reversible=matched_rule.get("reversible"),
        allow=not should_block,
        should_warn=bool(matched_rule.get("should_warn", True)),
        requires_confirmation=requires_confirmation or "user_confirmation" in required_context,
        should_block=should_block,
        required_context=required_context,
        recommended_confirmation_prompt=matched_rule.get("confirmation_prompt"),
        safer_alternative=matched_rule.get("safer_alternative"),
        reasons=reasons,
    )
