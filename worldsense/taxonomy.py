from __future__ import annotations

from functools import lru_cache
from typing import Any

from worldsense.rules import load_rule_file
from worldsense.schemas import RiskCategory


@lru_cache(maxsize=1)
def load_taxonomy() -> dict[RiskCategory, dict[str, Any]]:
    items = load_rule_file("taxonomy.yaml")
    taxonomy: dict[RiskCategory, dict[str, Any]] = {}
    for item in items:
        category = RiskCategory(item["category"])
        taxonomy[category] = item
    return taxonomy


def get_category_definition(category: RiskCategory | str) -> dict[str, Any]:
    parsed = category if isinstance(category, RiskCategory) else RiskCategory(category)
    return load_taxonomy()[parsed]

