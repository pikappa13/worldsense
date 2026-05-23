"""OpenAI adapter for WorldSense LLM-assisted analysis.

Install the OpenAI SDK separately:
    pip install openai

Usage:
    import openai
    from worldsense import RealityEngine
    from worldsense.adapters.openai_adapter import OpenAIAdapter

    client = openai.OpenAI()
    engine = RealityEngine(adapter=OpenAIAdapter(client))
    analysis = engine.analyze("Ho dormito 2 ore ma devo guidare 3 ore.")
"""

from __future__ import annotations

import json
from typing import Any

from worldsense.adapters.base import LLMMessage


class OpenAIAdapter:
    """Adapter for OpenAI chat completion models with JSON mode.

    The package does not depend on openai. Install it separately when using this adapter.
    """

    def __init__(self, client: Any, model: str = "gpt-4.1-mini") -> None:
        self.client = client
        self.model = model

    def complete_json(self, messages: list[LLMMessage]) -> dict:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": msg.role, "content": msg.content} for msg in messages],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
