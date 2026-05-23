from __future__ import annotations

import json
from typing import Any

from worldsense.adapters.base import LLMMessage


class OllamaAdapter:
    """Optional adapter for an injected Ollama-compatible client."""

    def __init__(self, client: Any, model: str = "llama3.1") -> None:
        self.client = client
        self.model = model

    def complete_json(self, messages: list[LLMMessage]) -> dict:
        response = self.client.chat(
            model=self.model,
            messages=[{"role": message.role, "content": message.content} for message in messages],
            format="json",
        )
        content = response["message"]["content"]
        return json.loads(content)

