"""Claude (Anthropic) adapter for WorldSense LLM-assisted analysis.

Install the Anthropic SDK separately:
    pip install anthropic

Usage:
    import anthropic
    from worldsense import RealityEngine
    from worldsense.adapters.claude_adapter import ClaudeAdapter

    client = anthropic.Anthropic()
    engine = RealityEngine(adapter=ClaudeAdapter(client))
    analysis = engine.analyze("Ho dormito 2 ore ma devo guidare 3 ore.")
"""

from __future__ import annotations

from typing import Any

from worldsense.adapters.base import LLMMessage


class ClaudeAdapter:
    """Adapter for Anthropic Claude models via the official SDK."""

    def __init__(
        self,
        client: Any,
        model: str = "claude-haiku-4-5-20251001",
        max_tokens: int = 1024,
    ) -> None:
        self.client = client
        self.model = model
        self.max_tokens = max_tokens

    def complete_json(self, messages: list[LLMMessage]) -> dict:
        system_prompt: str | None = None
        user_messages: list[dict[str, str]] = []

        for msg in messages:
            if msg.role == "system":
                system_prompt = msg.content
            else:
                user_messages.append({"role": msg.role, "content": msg.content})

        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": user_messages,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)
        text = response.content[0].text

        import json
        # Strip markdown code fences if the model wrapped the JSON
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(
                line for line in lines if not line.startswith("```")
            ).strip()

        return json.loads(text)
