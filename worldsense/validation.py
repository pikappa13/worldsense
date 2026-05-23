from __future__ import annotations

from pathlib import Path
from typing import Any

from worldsense.evaluation import load_scenarios
from worldsense.rules import load_action_rules, load_risk_rules
from worldsense.schemas import RiskCategory, RiskLevel, ValidationIssue, ValidationReport
from worldsense.taxonomy import load_taxonomy


def validate_project(seed_dataset_path: str | Path = "data/seed_scenarios.jsonl") -> ValidationReport:
    checked_files = [
        "worldsense/rules_data/risk_rules.yaml",
        "worldsense/rules_data/action_rules.yaml",
        "worldsense/rules_data/taxonomy.yaml",
        str(seed_dataset_path),
    ]
    issues: list[ValidationIssue] = []
    issues.extend(validate_risk_rules(load_risk_rules()))
    issues.extend(validate_action_rules(load_action_rules()))
    issues.extend(validate_taxonomy())
    issues.extend(validate_scenarios(seed_dataset_path))
    return ValidationReport(passed=not issues, checked_files=checked_files, issues=issues)


def validate_risk_rules(rules: list[dict[str, Any]]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    seen_ids: set[str] = set()
    required = {"id", "triggers", "risk_category", "min_risk_level", "consequences"}

    for rule in rules:
        rule_id = str(rule.get("id", ""))
        issues.extend(_missing_fields("risk_rules", rule, required, rule_id))
        if rule_id in seen_ids:
            issues.append(_issue("risk_rules", rule_id, "Duplicate rule id"))
        seen_ids.add(rule_id)

        _validate_enum(issues, "risk_rules", rule_id, RiskCategory, rule.get("risk_category"))
        _validate_enum(issues, "risk_rules", rule_id, RiskLevel, rule.get("min_risk_level"))
        keyword_groups = rule.get("triggers", {}).get("keyword_groups", [])
        if not keyword_groups or not all(isinstance(group, list) and group for group in keyword_groups):
            issues.append(_issue("risk_rules", rule_id, "triggers.keyword_groups must be non-empty"))
        if not isinstance(rule.get("consequences"), list) or not rule.get("consequences"):
            issues.append(_issue("risk_rules", rule_id, "consequences must be a non-empty list"))

    return issues


def validate_action_rules(rules: list[dict[str, Any]]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    seen_ids: set[str] = set()
    required = {"id", "action_type", "risk_level", "side_effect_type", "requires_context"}

    for rule in rules:
        rule_id = str(rule.get("id", ""))
        issues.extend(_missing_fields("action_rules", rule, required, rule_id))
        if rule_id in seen_ids:
            issues.append(_issue("action_rules", rule_id, "Duplicate rule id"))
        seen_ids.add(rule_id)

        _validate_enum(issues, "action_rules", rule_id, RiskLevel, rule.get("risk_level"))
        for category in rule.get("risk_categories", []):
            _validate_enum(issues, "action_rules", rule_id, RiskCategory, category)
        if rule.get("match_mode", "type_or_keyword") not in {"type_or_keyword", "type_and_keyword"}:
            issues.append(_issue("action_rules", rule_id, "Invalid match_mode"))

    return issues


def validate_taxonomy() -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    taxonomy = load_taxonomy()
    missing = set(RiskCategory) - set(taxonomy)
    extra = set(taxonomy) - set(RiskCategory)
    for category in sorted(missing, key=lambda item: item.value):
        issues.append(_issue("taxonomy", category.value, "Category missing from taxonomy"))
    for category in sorted(extra, key=lambda item: item.value):
        issues.append(_issue("taxonomy", category.value, "Unknown category in taxonomy"))
    for category, definition in taxonomy.items():
        for field in ["definition", "examples", "textual_signals", "minimum_risk_level", "mitigations"]:
            if field not in definition:
                issues.append(_issue("taxonomy", category.value, f"Missing field: {field}"))
        _validate_enum(
            issues,
            "taxonomy",
            category.value,
            RiskLevel,
            definition.get("minimum_risk_level"),
        )
    return issues


def validate_scenarios(path: str | Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    try:
        scenarios = load_scenarios(path)
    except ValueError as error:
        return [_issue(str(path), None, str(error))]

    seen_ids: set[str] = set()
    for scenario in scenarios:
        scenario_id = str(scenario.get("id", ""))
        if not scenario_id:
            issues.append(_issue(str(path), None, "Scenario is missing id"))
        if scenario_id in seen_ids:
            issues.append(_issue(str(path), scenario_id, "Duplicate scenario id"))
        seen_ids.add(scenario_id)

        if "action" not in scenario and "user_message" not in scenario:
            issues.append(_issue(str(path), scenario_id, "Scenario needs action or user_message"))
        _validate_enum(issues, str(path), scenario_id, RiskLevel, scenario.get("expected_risk_level"))
        for category in scenario.get("expected_categories", []):
            _validate_enum(issues, str(path), scenario_id, RiskCategory, category)
        if "expected_action" not in scenario:
            issues.append(_issue(str(path), scenario_id, "Scenario is missing expected_action"))

    return issues


def _missing_fields(
    source: str,
    item: dict[str, Any],
    fields: set[str],
    item_id: str | None,
) -> list[ValidationIssue]:
    return [_issue(source, item_id, f"Missing field: {field}") for field in sorted(fields - set(item))]


def _validate_enum(
    issues: list[ValidationIssue],
    source: str,
    item_id: str | None,
    enum_type: type[RiskCategory] | type[RiskLevel],
    value: Any,
) -> None:
    try:
        enum_type(value)
    except ValueError:
        issues.append(_issue(source, item_id, f"Invalid {enum_type.__name__}: {value}"))


def _issue(source: str, item_id: str | None, message: str) -> ValidationIssue:
    return ValidationIssue(source=source, item_id=item_id, message=message)
