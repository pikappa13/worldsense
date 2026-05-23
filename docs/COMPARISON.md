# How WorldSense Differs from Existing Tools

WorldSense occupies a distinct position in the AI tooling landscape. This document explains
what makes it different from the tools it is most often compared to.

**The core distinction:**
Most existing tools ask "is this content appropriate?" or "what should I do next?"
WorldSense asks "what will actually happen if this is done?"

---

## RAG (Retrieval-Augmented Generation)

| | RAG | WorldSense |
|---|---|---|
| **Primary function** | Retrieve relevant documents to ground LLM responses | Evaluate the real-world safety and plausibility of a response or action |
| **Input** | Query + document corpus | User message + optional response + optional planned action |
| **Output** | Augmented context for the LLM | Structured risk assessment with consequences and recommendations |
| **Requires external data** | Yes — a vector store or search index | No — works offline with YAML rules |
| **Knows about facts** | Yes — retrieves current information | No — does not retrieve facts |
| **Knows about consequences** | No | Yes — simulates likely outcomes |

**When to use RAG:** when the LLM needs factual grounding (current prices, documentation, news).

**When to use WorldSense:** when the LLM needs practical judgment (is this plan safe, is this
action reversible, is this response likely to cause harm).

**They compose well.** Use RAG to ground the response in facts, then WorldSense to check
whether acting on those facts is safe.

---

## Guardrails AI

| | Guardrails AI | WorldSense |
|---|---|---|
| **Primary function** | Validate LLM output structure and content against schemas and validators | Analyze real-world risk, consequences, and operational safety |
| **Approach** | Declarative validators (RAIL spec, Pydantic, regex) | Rule engine + optional LLM-assisted consequence simulation |
| **Focus** | Output format correctness, content policy compliance | Real-world plausibility, action safety, missing context |
| **Action gating** | No | Yes — dedicated module for agent tool use |
| **Consequence simulation** | No | Yes |
| **Social reasoning** | No | Yes |
| **Offline use** | Partially | Fully |

**When to use Guardrails AI:** when you need structured output validation, schema enforcement,
or content filtering on LLM responses.

**When to use WorldSense:** when you need to evaluate whether a response or action is
practically safe, contextually appropriate, and operationally sound.

**They compose well.** Guardrails AI validates the format and content of the response;
WorldSense validates the real-world implications of acting on it.

---

## LangChain

| | LangChain | WorldSense |
|---|---|---|
| **Primary function** | Orchestrate LLM pipelines, chains, and agents | Add a reality-check judgment layer to any LLM pipeline |
| **Scope** | Full application framework | Focused safety and judgment module |
| **Includes routing, memory, tools** | Yes | No — intentionally scoped |
| **Action safety** | No built-in gate | Yes — core feature |
| **Consequence simulation** | No | Yes |
| **Dependency footprint** | Large | Minimal (pydantic, PyYAML) |

**When to use LangChain:** when building complex multi-step LLM pipelines, chains, or agents.

**When to use WorldSense:** as a judgment layer inside or alongside a LangChain application
to add risk detection and action gating.

**They compose well.** WorldSense provides a `WorldSenseTool` (Phase 3 roadmap) that can
be used directly inside LangChain agents and chains.

---

## LlamaIndex

| | LlamaIndex | WorldSense |
|---|---|---|
| **Primary function** | Index and query documents; connect LLMs to data sources | Evaluate the safety and real-world implications of LLM outputs |
| **Data focus** | Strong — documents, databases, structured data | None — not a data layer |
| **Safety focus** | Minimal | Strong |
| **Action evaluation** | No | Yes |

**They serve different purposes and compose naturally.** LlamaIndex retrieves and structures
information; WorldSense evaluates the safety of acting on it.

---

## AutoGen / CrewAI / Multi-agent frameworks

| | AutoGen / CrewAI | WorldSense |
|---|---|---|
| **Primary function** | Coordinate multiple agents working toward a goal | Evaluate each agent's actions and outputs for safety |
| **Plans tasks** | Yes | No |
| **Executes actions** | Yes | No — only evaluates them |
| **Safety gate** | Not built-in | Core feature |
| **Can be added to agents** | N/A | Yes — as a pre-execution checker |

**When to use multi-agent frameworks:** when building systems where multiple agents collaborate.

**When to use WorldSense:** as a per-agent or per-action safety layer that runs before any
agent executes a tool or sends a response.

---

## Moderation APIs (OpenAI Moderation, Azure Content Safety, Perspective API)

| | Moderation APIs | WorldSense |
|---|---|---|
| **Primary function** | Classify text for toxic, harmful, or policy-violating content | Evaluate real-world risk, consequences, and operational safety |
| **Focus** | Content policy (hate speech, CSAM, violence, self-harm) | Practical judgment (is this plan feasible, is this action reversible) |
| **Requires API call** | Yes — external service | No — offline rule engine |
| **Detects implicit risk** | No — text-level classification | Yes — infers context and consequences |
| **Action gating** | No | Yes |
| **Understands context** | No — text in isolation | Yes — user message + response + action together |

**They address different problems.** Moderation APIs filter harmful content. WorldSense
evaluates whether a factually acceptable, policy-compliant response is nonetheless
practically dangerous or operationally unsound.

**Example:** The message "I need to resign today" passes every moderation filter. WorldSense
flags it as high-risk workplace/financial risk with missing context and recommends a
cooling-off period.

---

## Fact-checking tools

| | Fact-checkers | WorldSense |
|---|---|---|
| **Primary function** | Verify factual accuracy of claims | Evaluate practical safety and real-world consequences |
| **Checks facts** | Yes | No |
| **Checks plausibility** | Partially | Yes |
| **Detects overconfidence** | Sometimes | Yes — dedicated uncertainty module |
| **Evaluates consequences** | No | Yes |

**They are complementary.** Use a fact-checker to verify claims; use WorldSense to evaluate
whether acting on those claims is safe.

---

## Prompt templates / system prompts

Prompt engineering can partially address some of the problems WorldSense solves, but it has
structural limitations:

| | Prompt templates | WorldSense |
|---|---|---|
| **Inspectable** | No — reasoning is inside the LLM | Yes — structured JSON output |
| **Consistent** | No — LLM can ignore instructions | Yes — rule engine always fires |
| **Testable** | Hard — requires LLM call | Yes — deterministic tests |
| **Works offline** | No | Yes |
| **Model-agnostic** | Partially — tuned for specific models | Yes |
| **Adds latency** | Yes — longer prompts | Minimal for rule-based mode |

**When prompt engineering is enough:** simple, low-stakes conversational applications.

**When WorldSense adds value:** agent systems, tool use, high-stakes domains, applications
where you need to audit and test the safety layer independently of the LLM.

---

## Summary table

| Tool | What it does | What WorldSense does that it doesn't |
|------|-------------|--------------------------------------|
| RAG | Retrieves factual grounding | Evaluates consequences of acting on facts |
| Guardrails AI | Validates output format and content policy | Simulates real-world outcomes and action safety |
| LangChain | Orchestrates LLM pipelines | Adds judgment layer inside pipelines |
| LlamaIndex | Connects LLMs to data sources | Evaluates safety of using that data |
| AutoGen/CrewAI | Coordinates multi-agent systems | Gates each agent action for safety |
| Moderation APIs | Filters harmful content | Evaluates practical and operational risk |
| Fact-checkers | Verifies factual accuracy | Evaluates consequences regardless of accuracy |
| Prompt templates | Steers LLM behavior | Provides inspectable, testable, model-agnostic judgment |

WorldSense does not replace any of these tools. It fills the gap between "the LLM produced
a response" and "it is safe and practical to act on that response."
