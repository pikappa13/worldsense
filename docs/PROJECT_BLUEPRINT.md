# WorldSense Project Blueprint

WorldSense is a reality-check layer for AI systems. It sits around an LLM, chatbot, RAG app, or
tool-using agent and evaluates whether a proposed response or action is practical, safe, reversible,
socially appropriate, and sufficiently grounded in context.

## Vision

Modern language models are fluent, but fluency is not the same as operational judgment. A model can
produce text that sounds plausible while ignoring fatigue, travel time, data loss, social hierarchy,
missing constraints, financial cost, or irreversible side effects.

WorldSense is not another model. It is an external cognitive layer that analyzes:

- user prompts
- proposed responses
- planned tool actions
- conversation context
- agent goals
- missing information
- implicit constraints
- likely consequences
- reversibility
- real-world risk

## Non-Goals

WorldSense is not:

- an LLM
- a fact-checker only
- a RAG framework
- a moderation API
- a toxicity classifier
- a vector database
- a planner
- a prompt template collection

The core promise is narrower: inspect real-world plausibility and consequences before an AI responds
or acts.

## Problem Breakdown

### Missing implicit context

Users rarely provide all the details needed for a safe or useful answer. "I need to drive but I am
tired" implies safety risk, reduced reaction time, and possible underestimation of danger.

### Missing consequence simulation

AI systems often answer without asking: "What happens next if the user follows this?"
WorldSense tracks immediate, medium-term, reversible, irreversible, personal, social, technical,
legal, physical, and economic consequences.

### Missing risk hierarchy

A typo is not equivalent to deleting files, sending an angry email, giving unsafe medical guidance,
or running a destructive shell command. The engine explicitly ranks risk.

### Missing operational common sense

WorldSense checks time, fatigue, logistics, rollback, cost of failure, ambiguity, and social
friction.

### Missing action awareness

Agents that use tools need an action gate. Sending email, deleting files, buying products, changing
permissions, and publishing content are external side effects.

## Architecture

Pipeline:

1. Parse intent.
2. Extract implicit context.
3. Build world state.
4. Detect missing information.
5. Simulate consequences.
6. Classify risk.
7. Apply reality constraints.
8. Evaluate action safety.
9. Assess social context.
10. Detect unsupported assumptions.
11. Generate recommendations.
12. Produce structured JSON.
13. Optionally rewrite response guidance.

Pseudocode:

```python
intent = parse_intent(user_message)
implicit = extract_implicit_context(user_message, proposed_response)
world = build_world_state(user_message, implicit)
consequences = generate_consequences(user_message, proposed_response)
constraints = detect_constraint_violations(user_message, proposed_response)
action = evaluate_action(planned_action, context)
uncertainty = detect_uncertainty(user_message, proposed_response, implicit.missing_information)
risk = classify_risk(consequences, constraints, action, uncertainty)
recommendations = generate_recommendations(risk, action, triggered_rules)
return RealityAnalysis(...)
```

## Core Modules

- `intent.py`: simple intent parser for the rule-based MVP.
- `context.py`: implicit context extraction and world state construction.
- `consequences.py`: consequence generation from YAML rules.
- `risk.py`: risk scoring helpers.
- `constraints.py`: reality constraint checks such as impossible travel plans.
- `actions.py`: safety gate for agent tool use.
- `social.py`: social risk and tone analysis.
- `uncertainty.py`: missing context and unsupported confidence detection.
- `rewrite.py`: response rewrite guidance.
- `prompts.py`: internal prompts for optional LLM-assisted mode.
- `adapters/`: optional OpenAI and Ollama adapters.

## MVP Scope

The MVP is intentionally rule-based and useful without paid APIs. It includes:

- Python library
- CLI
- JSON/Pydantic output
- risk taxonomy
- action safety classifier
- consequence templates
- examples
- tests
- documentation
- optional LLM adapter interfaces

## Usage Modes

Library mode:

```python
analysis = engine.analyze(user_message="Ho dormito 2 ore ma devo guidare 3 ore.")
```

Response checking mode:

```python
analysis = engine.check_response(user_message="...", proposed_response="...")
```

Agent action mode:

```python
decision = engine.evaluate_action({"tool": "filesystem.delete", "target": "/tmp"})
```

CLI mode:

```bash
worldsense analyze "Ho dormito 2 ore ma devo guidare 3 ore."
```

Middleware mode:

```text
user -> LLM -> WorldSense -> final response
```

Tool safety mode:

```text
agent plans action -> WorldSense -> allow/warn/confirm/block
```

## Integrations

WorldSense can integrate with LangChain, LlamaIndex, AutoGen, CrewAI, MCP servers, OpenAI tool
calling, Ollama, and FastAPI by adding a check between generation and execution.

Minimal FastAPI shape:

```python
@app.post("/check")
def check(payload: dict):
    return engine.analyze(**payload).model_dump()
```

Minimal tool gate:

```python
decision = engine.evaluate_action(action, context)
if decision.should_block:
    raise PermissionError(decision.recommended_confirmation_prompt)
```

See `docs/INTEGRATIONS.md` for framework-specific examples.

## Differentiation

WorldSense differs from:

- RAG: it does not only retrieve information.
- Guardrails: it is not only schema validation.
- LangChain/LlamaIndex: it is not orchestration.
- Moderation APIs: it is not only content policy classification.
- Fact checkers: it evaluates consequences and missing context, not just truth.
- Planning agents: it checks plausibility and risk before action.

## Design Principles

1. Practicality over cleverness.
2. Detect consequences before generating advice.
3. Prefer uncertainty over false confidence.
4. Separate language fluency from real-world judgment.
5. Block irreversible actions unless context is clear.
6. Ask clarification only when necessary.
7. Preserve user autonomy.
8. Do not moralize unnecessarily.
9. Increase friction when risk is high.
10. Make reasoning inspectable.
11. Be model-agnostic.
12. Be useful without a large LLM.
13. Design for agents, not only chatbots.
14. Prefer structured outputs.
15. Fail safely.

## Roadmap

### Phase 0: Concept

- README
- taxonomy
- examples
- manifesto

### Phase 1: Rule-Based MVP

- engine
- YAML rules
- risk classifier
- action gate
- CLI
- tests

### Phase 2: LLM-Assisted Analysis

- OpenAI adapter
- Ollama adapter
- structured output prompts
- rule-based fallback

### Phase 3: Agent Safety

- tool policies
- irreversible action checks
- confirmation prompts
- sandbox suggestions

### Phase 4: Social Reasoning

- tone
- escalation
- hierarchy
- difficult communication

### Phase 5: Reality Planning

- logistics
- time
- fatigue
- travel
- task feasibility

### Phase 6: Community

- plugins
- benchmark
- dataset
- docs
- real-world examples

## Governance and License

WorldSense uses Apache-2.0 because it is permissive, business-friendly, and includes explicit patent
language. Future governance should include `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`,
issue templates, and a pull request template.

## Name

The recommended name is `WorldSense`. It communicates practical world awareness without claiming to
be a new foundation model. See `docs/NAMES.md` for alternatives and tradeoffs.

## Risks and Critique

The full vision can fail if it promises universal common sense. The project should avoid claiming
that it understands reality, provides professional advice, or guarantees safety. The small useful
version is a practical risk checker for agent actions and LLM responses.

Keep the first public claim grounded:

> WorldSense detects common hidden risks, missing context, and irreversible side effects before an
> AI system responds or acts.
