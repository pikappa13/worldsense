from __future__ import annotations

from functools import lru_cache
from importlib import resources
from typing import Any

import yaml


def normalize_text(value: str | None) -> str:
    return (value or "").casefold()


def keyword_matches(text: str, keywords: list[str]) -> bool:
    normalized = normalize_text(text)
    return all(keyword.casefold() in normalized for keyword in keywords)


@lru_cache(maxsize=16)
def load_rule_file(filename: str) -> list[dict[str, Any]]:
    rules_path = resources.files("worldsense.rules_data").joinpath(filename)
    with rules_path.open("r", encoding="utf-8") as file:
        loaded = yaml.safe_load(file) or []
    if not isinstance(loaded, list):
        raise ValueError(f"Rule file {filename} must contain a YAML list")
    return loaded


def load_risk_rules() -> list[dict[str, Any]]:
    return load_rule_file("risk_rules.yaml")


def load_action_rules() -> list[dict[str, Any]]:
    return load_rule_file("action_rules.yaml")

