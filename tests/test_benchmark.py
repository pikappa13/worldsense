from pathlib import Path

from worldsense.evaluation import run_benchmark
from worldsense.taxonomy import load_taxonomy
from worldsense.schemas import RiskCategory


def test_seed_benchmark_passes_current_rules() -> None:
    report = run_benchmark(Path("data/seed_scenarios.jsonl"))

    assert report.total == 20
    assert report.pass_rate == 1.0


def test_taxonomy_loads_all_declared_categories() -> None:
    taxonomy = load_taxonomy()

    assert RiskCategory.PHYSICAL_SAFETY in taxonomy
    assert len(taxonomy) == len(RiskCategory)
