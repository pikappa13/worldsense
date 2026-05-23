# WorldSense

A reality-check layer for AI agents.

WorldSense is an open source Python library that helps LLM apps and AI agents detect hidden
risks, missing context, irreversible actions, and real-world consequences before they answer or
act.

Fluent text is not the same thing as good judgment. WorldSense is designed to sit around an LLM,
chatbot, coding agent, RAG app, or tool-using agent and add a practical judgment pass.

## What it is

WorldSense analyzes:

- user messages
- proposed LLM responses
- planned agent actions
- available context
- implicit constraints
- likely consequences
- missing information
- operational and social risk

It returns structured, machine-readable output with a risk level, triggered categories,
consequences, recommendations, and optional action gating.

## What it is not

WorldSense is not an LLM, a vector database, a RAG framework, a moderation API, a prompt template,
or a replacement for domain experts. The MVP is intentionally rule-based and inspectable, with
optional LLM adapters planned later.

## Install

```bash
pip install worldsense
```

For local development:

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from worldsense import RealityEngine

engine = RealityEngine()

analysis = engine.analyze(
    user_message="Ho dormito 2 ore ma devo guidare 3 ore.",
    proposed_response="Fai delle pause e bevi un caffe.",
)

print(analysis.risk.risk_level)
print(analysis.recommendations)
```

Agent action gate:

```python
from worldsense import RealityEngine

engine = RealityEngine()

decision = engine.evaluate_action(
    action={
        "tool": "filesystem.delete",
        "target": "/project/temp",
        "description": "Delete temporary files",
    },
    context={"project_path": "/project", "user_confirmation": False},
)

if decision.should_block:
    print(decision.recommended_confirmation_prompt)
```

## CLI

```bash
worldsense analyze "Ho dormito 2 ore ma devo guidare 3 ore." \
  --response "Fai delle pause e bevi un caffe."
```

```bash
worldsense action "{\"tool\":\"filesystem.delete\",\"target\":\"/tmp/data\"}"
```

PowerShell-friendly form:

```bash
worldsense action --tool filesystem.delete --target /tmp/data --description "Delete temporary files"
```

Run the seed benchmark:

```bash
worldsense benchmark data/seed_scenarios.jsonl
```

The bundled seed benchmark currently covers 20 scenarios across destructive actions, travel
realism, social escalation, medical urgency, privacy, overconfidence, and missing context.

## Core Concepts

- Intent parsing: identify what the user or agent is trying to do.
- Implicit context extraction: surface constraints the user did not spell out.
- Consequence simulation: list likely practical consequences.
- Risk classification: classify severity using a consistent taxonomy.
- Reality constraints: detect unrealistic plans and unsafe operational assumptions.
- Action safety gate: block or require confirmation for risky tool use.
- Uncertainty detection: flag missing context and unsupported confidence.
- Rewrite guidance: suggest how an LLM response should become safer and more practical.

## Documentation

- [Project blueprint](docs/PROJECT_BLUEPRINT.md)
- [Risk taxonomy](docs/TAXONOMY.md)
- [Practical examples](docs/EXAMPLES.md)
- [Internal LLM prompts](docs/INTERNAL_PROMPTS.md)
- [Project name options](docs/NAMES.md)
- [Benchmark plan](benchmark/README.md)
- [Seed dataset](data/seed_scenarios.jsonl)

## Initial Risk Categories

WorldSense starts with a small but extensible taxonomy:

- physical_safety
- medical
- mental_health
- legal
- financial
- privacy
- cybersecurity
- data_loss
- reputation
- social_conflict
- workplace
- relationship
- travel_logistics
- operational
- irreversible_action
- public_communication
- child_safety
- third_party_harm
- misinformation
- overconfidence
- missing_context

## Roadmap

1. Rule-based MVP with YAML rules, Pydantic schemas, CLI, tests, and examples.
2. Optional LLM-assisted analysis with structured JSON output.
3. Agent framework integrations for LangChain, LlamaIndex, CrewAI, AutoGen, MCP, and OpenAI tool calling.
4. Benchmark dataset for destructive actions, missing context, physical safety, social escalation, and overconfidence.
5. Community rule packs and domain-specific adapters.

## Design Principles

- Practicality over cleverness.
- Detect consequences before generating advice.
- Prefer uncertainty over false confidence.
- Block irreversible actions unless context is clear.
- Preserve user autonomy.
- Make reasoning inspectable.
- Be useful without paid APIs.
- Fail safely.

## Status

WorldSense is early alpha. The first version is deliberately conservative and rule-based. It is
meant to be understandable, testable, and easy to extend.

## Disclaimer

WorldSense is a developer tool for risk awareness and action gating. It does not provide medical,
legal, financial, or safety guarantees. High-risk domains still require qualified human judgment.

## License

Apache-2.0
