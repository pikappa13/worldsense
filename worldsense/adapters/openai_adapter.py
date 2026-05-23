from __future__ import annotations

import json
from typing import Any

from worldsense.adapters.base import LLMMessage


class OpenAIAdapter:
    """Small optional adapter for OpenAI chat-style JSON calls.

    The package does not depend on openai. Install it separately when using this adapter.
    """

    def __init__(self, client: Any, model: str = "gpt-4.1-mini") -> None:
        self.client = client
        self.model = model

    def complete_json(self, messages: list[LLMMessage]) -> dict:
        response = self.client.responses.create(
            model=self.model,
            input=[{"role": message.role, "content": message.content} for message in messages],
            text={"format": {"type": "json_object"}},
        )
        return json.loads(response.output_text)

