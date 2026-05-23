# Internal LLM Prompts

WorldSense works without LLM calls. Optional LLM mode should use strict JSON prompts and keep the
rule-based engine as fallback.

The canonical prompt strings live in `worldsense/prompts.py`:

- `ANALYZE_IMPLICIT_CONTEXT_PROMPT`
- `SIMULATE_CONSEQUENCES_PROMPT`
- `CLASSIFY_RISK_PROMPT`
- `REWRITE_RESPONSE_PROMPT`

Prompt rules:

- Return valid JSON only.
- Separate facts from assumptions.
- Do not invent missing details.
- Surface uncertainty.
- Prefer safer alternatives when risk is high.
- Do not moralize.

