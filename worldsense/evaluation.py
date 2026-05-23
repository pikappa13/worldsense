from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from worldsense.engine import RealityEngine
from worldsense.risk import RISK_ORDER
from worldsense.schemas import BenchmarkReport, RiskCategory, RiskLevel, ScenarioEvaluation


def load_scenarios(path: str | Path) -> list[dict[str, Any]]:
    scenario_path = Path(path)
    scenarios: list[dict[str, Any]] = []
    for line_number, line in enumerate(scenario_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            scenarios.append(json.loads(line))
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid JSONL at {scenario_path}:{line_number}") from error
    return scenarios


def run_benchmark(path: str | Path, engine: RealityEngine | None = None) -> BenchmarkReport:
    engine = engine or RealityEngine()
    results = [_evaluate_scenario(engine, scenario) for scenario in load_scenarios(path)]
    passed = sum(1 for result in results if result.passed)
    total = len(results)
    return BenchmarkReport(
        total=total,
        passed=passed,
        failed=total - passed,
        pass_rate=passed / total if total else 0.0,
        results=results,
    )


def _evaluate_scenario(engine: RealityEngine, scenario: dict[str, Any]) -> ScenarioEvaluation:
    if "action" in scenario:
        assessment = engine.evaluate_action(scenario["action"], scenario.get("context"))
        actual_risk = assessment.risk_level
        actual_categories = assessment.categories
        actual_missing = assessment.required_context
        actual_actions = _actions_from_assessment(assessment)
    else:
        analysis = engine.analyze(
            user_message=scenario.get("user_message", ""),
            proposed_response=scenario.get("proposed_response"),
            context=scenario.get("context"),
        )
        actual_risk = analysis.risk.risk_level
        actual_categories = analysis.risk.categories
        actual_missing = sorted(
            set(analysis.implicit_context.missing_information)
            | set(
                analysis.uncertainty_assessment.missing_context
                if analysis.uncertainty_assessment
                else []
            )
        )
        actual_actions = [recommendation.action for recommendation in analysis.recommendations]

    expected_risk = RiskLevel(scenario["expected_risk_level"])
    expected_categories = [RiskCategory(category) for category in scenario.get("expected_categories", [])]
    expected_missing = list(scenario.get("expected_missing_info", []))
    expected_action = scenario.get("expected_action")

    risk_met = RISK_ORDER[actual_risk] >= RISK_ORDER[expected_risk]
    categories_met = not expected_categories or bool(set(expected_categories) & set(actual_categories))
    missing_context_met = not expected_missing or bool(set(expected_missing) & set(actual_missing))
    action_met = expected_action is None or _expected_action_matches(expected_action, actual_actions)

    notes: list[str] = []
    if not risk_met:
        notes.append("actual risk is below expected risk")
    if not categories_met:
        notes.append("no expected category was detected")
    if not missing_context_met:
        notes.append("no expected missing-context signal was detected")
    if not action_met:
        notes.append("expected action was not reflected in recommendations")

    return ScenarioEvaluation(
        scenario_id=scenario["id"],
        passed=risk_met and categories_met and missing_context_met and action_met,
        risk_met=risk_met,
        categories_met=categories_met,
        missing_context_met=missing_context_met,
        expected_risk_level=expected_risk,
        actual_risk_level=actual_risk,
        expected_categories=expected_categories,
        actual_categories=actual_categories,
        expected_missing_context=expected_missing,
        actual_missing_context=actual_missing,
        expected_action=expected_action,
        actual_actions=actual_actions,
        notes=notes,
    )


def _actions_from_assessment(assessment: Any) -> list[str]:
    actions: list[str] = []
    if assessment.should_block:
        actions.append("block")
    if assessment.requires_confirmation:
        actions.append("require_confirmation")
    if assessment.should_warn:
        actions.append("warn")
    if assessment.allow and not actions:
        actions.append("allow")
    return actions


def _expected_action_matches(expected_action: str, actual_actions: list[str]) -> bool:
    if expected_action in actual_actions:
        return True
    expected_tokens = set(expected_action.replace("-", "_").split("_"))
    for action in actual_actions:
        action_tokens = set(action.replace("-", "_").split("_"))
        if expected_tokens & action_tokens:
            return True
    if expected_action.startswith("warn") and "warn" in actual_actions:
        return True
    if "confirm" in expected_action and "require_confirmation" in actual_actions:
        return True
    if expected_action.startswith("block") and "block" in actual_actions:
        return True
    if expected_action.startswith("ask") and any(action.startswith("ask") for action in actual_actions):
        return True
    if expected_action.startswith("refuse") and "block" in actual_actions:
        return True
    return False
