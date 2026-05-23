"""Optional LLM adapters for WorldSense."""

from worldsense.adapters.base import LLMAdapter, LLMMessage

__all__ = ["LLMAdapter", "LLMMessage"]


def get_claude_adapter(model: str = "claude-haiku-4-5-20251001"):
    """Return a ClaudeAdapter with an auto-created Anthropic client.

    Requires: pip install worldsense[claude]
    The ANTHROPIC_API_KEY env var must be set.
    """
    try:
        import anthropic  # type: ignore[import]
    except ImportError as exc:
        raise ImportError("Install the Anthropic SDK: pip install worldsense[claude]") from exc
    from worldsense.adapters.claude_adapter import ClaudeAdapter
    return ClaudeAdapter(anthropic.Anthropic(), model=model)


def get_openai_adapter(model: str = "gpt-4.1-mini"):
    """Return an OpenAIAdapter with an auto-created OpenAI client.

    Requires: pip install worldsense[openai]
    The OPENAI_API_KEY env var must be set.
    """
    try:
        import openai  # type: ignore[import]
    except ImportError as exc:
        raise ImportError("Install the OpenAI SDK: pip install worldsense[openai]") from exc
    from worldsense.adapters.openai_adapter import OpenAIAdapter
    return OpenAIAdapter(openai.OpenAI(), model=model)


def get_ollama_adapter(model: str = "llama3.1"):
    """Return an OllamaAdapter with an auto-created Ollama client.

    Requires: pip install worldsense[ollama]
    Ollama must be running locally.
    """
    try:
        import ollama  # type: ignore[import]
    except ImportError as exc:
        raise ImportError("Install the Ollama client: pip install worldsense[ollama]") from exc
    from worldsense.adapters.ollama_adapter import OllamaAdapter
    return OllamaAdapter(ollama.Client(), model=model)

