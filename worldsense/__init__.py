"""WorldSense: a reality-check layer for AI agents."""

from worldsense.engine import RealityEngine
from worldsense.evaluation import run_benchmark
from worldsense.schemas import ActionAssessment, RealityAnalysis, RiskLevel
from worldsense.taxonomy import get_category_definition, load_taxonomy
from worldsense.validation import validate_project

__all__ = [
    "ActionAssessment",
    "RealityAnalysis",
    "RealityEngine",
    "RiskLevel",
    "get_category_definition",
    "load_taxonomy",
    "run_benchmark",
    "validate_project",
]

# Convenience: expose adapter factory helpers at top level
# Usage: from worldsense import get_claude_adapter
def get_claude_adapter(model: str = "claude-haiku-4-5-20251001"):
    """Return a ClaudeAdapter. Requires: pip install worldsense[claude]"""
    from worldsense.adapters import get_claude_adapter as _f
    return _f(model=model)


def get_openai_adapter(model: str = "gpt-4.1-mini"):
    """Return an OpenAIAdapter. Requires: pip install worldsense[openai]"""
    from worldsense.adapters import get_openai_adapter as _f
    return _f(model=model)


def get_ollama_adapter(model: str = "llama3.1"):
    """Return an OllamaAdapter. Requires: pip install worldsense[ollama]"""
    from worldsense.adapters import get_ollama_adapter as _f
    return _f(model=model)
