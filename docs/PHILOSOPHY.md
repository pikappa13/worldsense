# WorldSense Design Philosophy

WorldSense is built on 15 explicit principles. They are not aspirational slogans — each one
reflects a concrete trade-off made during design and a specific failure mode it prevents.

---

## 1. Practicality over cleverness

The goal is not to build an impressive system. It is to catch real mistakes before they reach
users. A rule that detects "I haven't slept" is more valuable than a sophisticated neural
classifier that catches the same thing 5% better. When in doubt, choose the simpler solution
that works reliably.

**What this prevents:** over-engineering, hallucinated sophistication, systems that work in
demos but fail in production.

---

## 2. Detect consequences before generating advice

An AI that gives advice without simulating consequences is guessing. WorldSense always asks
"what happens next?" before producing recommendations. Consequences are the primary output;
recommendations are derived from them.

**What this prevents:** advice that sounds reasonable but leads to harm; responses that
address the surface request while ignoring the downstream impact.

---

## 3. Prefer uncertainty over false confidence

When information is missing, say so. When a claim is unverifiable, flag it. A response
that honestly says "I don't know if this is safe" is more useful than one that confidently
gives wrong guidance. Uncertainty is data.

**What this prevents:** overconfident recommendations in ambiguous situations; the AI acting
as if it has context it doesn't have.

---

## 4. Separate language fluency from real-world judgment

A grammatically perfect sentence can describe an impossible plan. A polite email can
still escalate a conflict. Fluency and correctness are orthogonal to safety and practicality.
WorldSense treats them separately — it does not try to improve writing quality, it evaluates
real-world plausibility.

**What this prevents:** confusing "well-written response" with "safe response"; assuming
that if an LLM sounds confident, the underlying plan is sound.

---

## 5. Block irreversible actions unless context is clear

Reversible mistakes can be corrected. Irreversible ones cannot. File deletion, database drops,
sent emails, published content, financial transactions — these require a higher bar. If the
context is ambiguous, block first and ask for confirmation.

**What this prevents:** data loss, financial harm, and reputational damage from agents that
act without fully understanding the consequences of permanent actions.

---

## 6. Ask for clarification only when necessary

Asking too many questions degrades the user experience and signals that the system is
incapable. WorldSense only requests clarification when missing information materially changes
the risk assessment — not as a reflexive safety net.

**What this prevents:** question fatigue; systems that ask about everything and therefore
teach users to click through confirmations without reading them.

---

## 7. Preserve user autonomy

WorldSense warns, flags, and recommends — it does not decide on behalf of the user. The
user is the final authority. Even for high-risk situations, the output is structured to
inform the decision, not to replace it. Hard blocks are reserved for actions where the
harm is clear, irreversible, and not justified by any plausible context.

**What this prevents:** paternalistic AI that refuses reasonable requests; systems that
frustrate users with unnecessary friction.

---

## 8. Do not moralize unnecessarily

Risk assessment is not a moral lecture. WorldSense reports consequences and probabilities
objectively. It does not add unsolicited ethical commentary, shame users for their choices,
or repeat warnings the user has already acknowledged.

**What this prevents:** preachy AI that alienates users; warning fatigue that causes users
to ignore legitimate risk signals.

---

## 9. Increase friction when risk is high

Low-risk situations should flow smoothly. High-risk situations deserve friction. The amount
of friction — a warning, a confirmation request, a hard block — should be proportional to
the severity and irreversibility of the risk, not applied uniformly to everything.

**What this prevents:** alert fatigue (uniform friction); catastrophic mistakes (no friction).

---

## 10. Make reasoning inspectable

Every risk assessment should be traceable. Which rules fired? Which consequences were
simulated? Why was this classified as "high" rather than "medium"? The structured JSON
output is designed to be readable by both developers and downstream systems. No black boxes.

**What this prevents:** unexplainable AI decisions; inability to debug false positives or
false negatives; distrust from users who can't see why something was flagged.

---

## 11. Be model-agnostic

WorldSense should work with any LLM — Claude, GPT-4, Llama, Mistral, or no LLM at all.
The rule-based core is the foundation. LLM adapters are optional enhancements. No feature
should require a specific commercial API.

**What this prevents:** vendor lock-in; inability to use the library in offline, local, or
cost-sensitive environments.

---

## 12. Be useful without a large LLM

The MVP must work with zero API calls. The YAML rule engine is not a fallback — it is the
primary tier. LLM-assisted analysis is an upgrade, not a requirement. This makes WorldSense
deployable in air-gapped environments, low-cost setups, and CI pipelines without external
dependencies.

**What this prevents:** dependency on paid APIs; breaking changes when API providers change
pricing or availability; inability to test deterministically.

---

## 13. Design for agents, not only chatbots

Most safety tooling is designed for conversational interfaces. WorldSense is built for
agents that use tools — filesystem operations, API calls, shell commands, database writes.
The action safety gate is a first-class feature, not an afterthought.

**What this prevents:** unsafe autonomous agents that execute destructive operations without
appropriate context or confirmation.

---

## 14. Prefer structured outputs

Every WorldSense output is a typed Pydantic model serializable to JSON. No free-form text
that requires parsing. Downstream systems — agents, middleware, dashboards — should be able
to consume WorldSense output programmatically without string matching or prompt engineering.

**What this prevents:** brittle integrations; outputs that are useful for humans but
useless for automated systems.

---

## 15. Fail safely

If WorldSense itself encounters an error — a malformed rule, a failed LLM call, an
unexpected input — it should degrade gracefully rather than crash the calling application.
LLM adapter failures fall back to the rule-based engine. Rule loading errors produce empty
results, not exceptions. The system is a safety layer; it must not itself become a source
of failure.

**What this prevents:** WorldSense outages taking down the systems it is supposed to protect;
partial failures causing incorrect risk assessments instead of safe defaults.
