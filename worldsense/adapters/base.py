from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LLMMessage:
    role: str
    content: str


class LLMAdapter(Protocol):
    def complete_json(self, messages: list[LLMMessage]) -> dict:
        """Return a JSON-compatible dictionary from an LLM provider."""

