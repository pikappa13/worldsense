# WorldSense

**A reality-check layer for AI agents — detect hidden risks, missing context, and real-world consequences before your LLM answers or acts.**

[![PyPI](https://img.shields.io/pypi/v/worldsense)](https://pypi.org/project/worldsense/)
[![Python](https://img.shields.io/pypi/pyversions/worldsense)](https://pypi.org/project/worldsense/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![CI](https://github.com/pikappa13/worldsense/actions/workflows/ci.yml/badge.svg)](https://github.com/pikappa13/worldsense/actions)

WorldSense is an open source Python library and MCP server that wraps any LLM, chatbot, coding
agent, or RAG app and adds a practical judgment pass before it answers or acts.

It catches what language models miss: **fatigue and logistical constraints, irreversible actions,
implicit social risk, overconfident claims, and dangerous tool use** — returning a structured
JSON analysis with risk level, consequences, and rewrite guidance.

> "Fluent text is not the same thing as good judgment."

**Works as:**
- a Python library (`pip install worldsense`)
- an MCP tool for **Claude Code**, **Cursor**, and **Claude Desktop** (zero extra code)
- a CLI (`worldsense analyze "..."`)
- an optional LLM-backed analyzer (Claude, OpenAI, Ollama)

## Why WorldSense?

Most LLMs are excellent at generating fluent text but poor at practical judgment:

- A coding agent deletes the wrong files because it doesn't understand irreversibility
- A travel assistant proposes a physically impossible itinerary
- A chatbot gives a dangerously overconfident medical answer
- An AI replies to your boss in a tone that escalates the conflict

WorldSense is a **modular judgment layer** you attach to any AI system to catch these problems
before they reach the user.

## What it analyzes

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

## Use as an MCP tool (Claude Code, Cursor, Claude Desktop)

WorldSense ships a built-in MCP server. Once registered, any MCP-compatible AI can call
WorldSense tools natively — no extra code required.

### Claude Code

Add this to your project's `.claude/settings.json` (or `~/.claude/settings.json` for global use):

```json
{
  "mcpServers": {
    "worldsense": {
      "command": "worldsense",
      "args": ["mcp"]
    }
  }
}
```

Restart Claude Code. Three tools become available:

| Tool | What it does |
|------|-------------|
| `worldsense_analyze` | Analyze a message for hidden risks, missing context, and real-world consequences |
| `worldsense_evaluate_action` | Gate a destructive action (file delete, shell command, API call…) before execution |
| `worldsense_check_response` | Check a draft AI response for overconfidence, social risk, and unsafe advice |

You can ask Claude to use them explicitly:

> "Before deleting those files, run `worldsense_evaluate_action` to check if it's safe."

Or add this to your `CLAUDE.md` to make it automatic for every project:

```markdown
## Safety policy

Before executing any destructive action (file deletion, shell commands, database writes,
API calls with side effects), call `worldsense_evaluate_action` and respect the result:
- `should_block: true` → do not proceed, explain why to the user
- `requires_confirmation: true` → ask the user before proceeding
- `should_warn: true` → show the warning, then proceed if the user confirms

Before answering questions with real-world risk (medical, legal, financial, physical safety),
call `worldsense_analyze` on the user message and incorporate the `rewrite_guidance`
into your response.
```

### Cursor

In `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "worldsense": {
      "command": "worldsense",
      "args": ["mcp"]
    }
  }
}
```

### Claude Desktop

In `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "worldsense": {
      "command": "worldsense",
      "args": ["mcp"]
    }
  }
}
```

Full MCP documentation: [docs/MCP_SERVER.md](docs/MCP_SERVER.md)

---

## Use with an LLM backend (Claude / OpenAI / Ollama)

By default WorldSense works offline with YAML rules. Pass an adapter to enable
LLM-assisted context extraction and consequence simulation:

```bash
pip install "worldsense[claude]"   # Anthropic Claude
pip install "worldsense[openai]"   # OpenAI
pip install "worldsense[ollama]"   # Ollama (local)
```

```python
from worldsense import RealityEngine, get_claude_adapter

engine = RealityEngine(adapter=get_claude_adapter())
analysis = engine.analyze("Ho dormito 2 ore ma devo guidare 3 ore.")
```

The rule-based core always runs first. The LLM enriches context extraction and consequence
simulation on top. If the LLM call fails, the engine falls back to rules silently.

---

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

Validate rules, taxonomy, and dataset:

```bash
worldsense validate
```

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

**Understanding WorldSense**
- [Design philosophy](docs/PHILOSOPHY.md) — 15 explicit principles behind every decision
- [Comparison with other tools](docs/COMPARISON.md) — how WorldSense differs from RAG, Guardrails, LangChain, moderation APIs, and more
- [Honest critique](docs/CRITIQUES.md) — limitations, risks, and what not to claim
- [Project blueprint](docs/PROJECT_BLUEPRINT.md) — detailed architecture

**Using WorldSense**
- [Integrations](docs/INTEGRATIONS.md) — LangChain, LlamaIndex, AutoGen, CrewAI, FastAPI, OpenAI, Ollama
- [MCP server](docs/MCP_SERVER.md) — Claude Code, Cursor, Claude Desktop setup
- [Practical examples](docs/EXAMPLES.md) — 10 full input/output walkthroughs
- [Risk taxonomy](docs/TAXONOMY.md) — 21 categories with definitions and signals

**Contributing**
- [Roadmap](ROADMAP.md) — phases 0–6 with current status
- [Benchmark plan](benchmark/README.md) — evaluation categories and metrics
- [Seed dataset](data/seed_scenarios.jsonl) — 20 annotated scenarios
- [Internal LLM prompts](docs/INTERNAL_PROMPTS.md)

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

- [x] Rule-based MVP — YAML rules, Pydantic schemas, CLI, tests, and examples
- [x] MCP server — use WorldSense as a native tool in Claude Code, Cursor, and Claude Desktop
- [x] LLM adapters — Claude, OpenAI, and Ollama backends for richer analysis
- [x] Benchmark dataset — 20 seed scenarios, 100% CI pass rate
- [ ] Agent framework integrations — LangChain, LlamaIndex, CrewAI, AutoGen
- [ ] Extended rule packs — domain-specific rules contributed by the community
- [ ] Multi-turn context tracking — carry risk state across conversation turns
- [ ] Analytics — aggregate risk patterns across sessions

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

## Contributing

Contributions are welcome — new rules, new adapters, benchmark scenarios, translations.
See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache-2.0

---

<!-- search keywords: AI safety, LLM guardrails, agent safety, MCP tool, risk detection,
consequence simulation, common sense AI, reality check AI, Claude Code tool, AI judgment,
responsible AI, LLM safety layer, AI agent guardrails, tool use safety, action gating -->
