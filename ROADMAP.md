# WorldSense Roadmap

This document describes the planned development phases for WorldSense.
Each phase is designed to be independently useful — earlier phases are not placeholders,
they are production-ready deliverables.

---

## Phase 0 — Concept ✅

**Goal:** Define the problem space precisely enough to build something real.

- [x] Risk taxonomy — 21 categories with definitions, signals, and mitigations
- [x] Design principles — 15 explicit principles guiding all decisions
- [x] Project name and identity — WorldSense
- [x] README and manifesto — explain the problem and the approach
- [x] Practical examples — 10 concrete input/output scenarios
- [x] Comparison with existing tools — explain what WorldSense is not

---

## Phase 1 — MVP rule-based ✅

**Goal:** A working, installable library with no external API dependencies.

- [x] `RealityEngine` class with full 10-step pipeline
- [x] YAML rule system — `risk_rules.yaml`, `action_rules.yaml`
- [x] Risk classifier — 5 levels (none/low/medium/high/critical)
- [x] Action safety gate — block/warn/require_confirmation/allow
- [x] Pydantic schemas — all 12 typed output models
- [x] CLI — `worldsense analyze / action / benchmark / validate`
- [x] Test suite — 50+ tests, 100% benchmark pass rate
- [x] Seed benchmark dataset — 20 JSONL scenarios
- [x] PyPI package — `pip install worldsense`
- [x] Documentation — README, blueprint, taxonomy, examples

---

## Phase 2 — LLM-assisted analysis ✅

**Goal:** Optional LLM backends for richer, generative analysis on top of the rule base.

- [x] Adapter protocol — `LLMAdapter` base class
- [x] Claude adapter — Anthropic SDK integration
- [x] OpenAI adapter — GPT-4 / GPT-4o integration
- [x] Ollama adapter — local model support
- [x] LLM-assisted context extraction — replaces keyword matching
- [x] LLM-assisted consequence simulation — enriches rule output
- [x] LLM-assisted rewrite guidance — generates safer response framing
- [x] Silent fallback — LLM failures fall back to rule engine
- [x] `pip install worldsense[claude|openai|ollama]` extras

---

## Phase 3 — MCP server and agent tool integrations ✅

**Goal:** Use WorldSense as a native tool inside AI coding assistants and agent frameworks.

- [x] MCP server — JSON-RPC 2.0 over stdin/stdout
- [x] `worldsense_analyze` MCP tool
- [x] `worldsense_evaluate_action` MCP tool
- [x] `worldsense_check_response` MCP tool
- [x] Claude Code integration — `.claude/settings.json` registration
- [x] Cursor integration — `~/.cursor/mcp.json` registration
- [x] Claude Desktop integration
- [x] `worldsense mcp` CLI entrypoint
- [ ] OpenAI function calling definitions (JSON schema for tool use)
- [ ] LangChain tool wrapper — `WorldSenseTool` for chains and agents
- [ ] LlamaIndex tool adapter
- [ ] CrewAI tool integration
- [ ] AutoGen integration
- [ ] FastAPI middleware — plug WorldSense between request and LLM response

---

## Phase 4 — Social reasoning and communication safety

**Goal:** Deeper analysis of human communication scenarios — tone, hierarchy, conflict,
cultural context.

- [ ] Extended social rules — boss/manager, client, partner, family, public
- [ ] Escalation detection — flag responses likely to worsen a conflict
- [ ] Tone classifier — formal/informal/aggressive/passive-aggressive
- [ ] Power asymmetry detection — identify hierarchy mismatches
- [ ] Cultural context hints — flag region/context-sensitive communication risks
- [ ] Relationship risk scoring — distinguish professional from personal contexts
- [ ] `SocialRuleEngine` — dedicated YAML pack for social scenarios
- [ ] 20+ new benchmark scenarios for social escalation

---

## Phase 5 — Reality planning and logistics constraints

**Goal:** Detect physically impossible or operationally unrealistic plans.

- [ ] Travel time validator — check itinerary feasibility against real distances
- [ ] Cognitive load estimator — flag plans with too many parallel tasks
- [ ] Human fatigue modeling — sleep deprivation, working hours, attention limits
- [ ] Budget constraint detection — flag plans missing financial context
- [ ] Time feasibility checker — deadlines vs. realistic effort estimates
- [ ] Dependency graph — detect circular dependencies in plans
- [ ] 20+ benchmark scenarios for logistics and planning realism
- [ ] `PlanningConstraintEngine` — modular extension for planning agents

---

## Phase 6 — Community, ecosystem, and extensibility

**Goal:** Make WorldSense a living project with community contributions and broad ecosystem
coverage.

- [ ] Community rule packs — domain-specific YAML bundles (medical, legal, finance, DevOps)
- [ ] Rule contribution guide — how to write, test, and submit new rules
- [ ] Rule registry — versioned, community-maintained rule packs
- [ ] Plugin architecture — register custom analyzers without forking
- [ ] Extended benchmark dataset — 100+ scenarios across all categories
- [ ] Benchmark leaderboard — compare rule packs and adapter configurations
- [ ] Analytics API — aggregate risk patterns across sessions
- [ ] Dashboard (optional) — visualize risk distribution in a project
- [ ] Language packs — non-English rule sets (Italian, Spanish, French, German)
- [ ] `worldsense hub` — CLI command to install community rule packs

---

## Versioning policy

WorldSense follows [Semantic Versioning](https://semver.org/):

- **0.x** — API may change. Rule format may change. Use with pinned versions.
- **1.0** — Stable public API. Rule format frozen. Adapters and plugins are stable.

The benchmark pass rate is part of the release contract: no version is released with a
benchmark pass rate below 100% on the seed dataset.

---

## How to contribute to the roadmap

Open an issue or discussion on GitHub to propose new features, rule packs, integrations,
or benchmark scenarios. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.
