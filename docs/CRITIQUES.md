# Honest Assessment: Risks and Limitations of WorldSense

This document is written in bad faith toward the project — intentionally. Its purpose is to
articulate the strongest criticisms of WorldSense so that contributors and users can make
informed decisions, and so that the project avoids making promises it cannot keep.

---

## Why this project might fail

### 1. The rule-based core has fundamental coverage limits

Keyword matching is fragile. The current implementation fires on "stanco" and "guidare" to
detect driving fatigue. It will miss:

- Paraphrases: "I'm exhausted and need to drive"
- Implicit context: "I've been awake since yesterday"
- Languages it wasn't designed for
- Novel scenarios not covered by existing rules

**The honest limit:** the rule engine is a demonstration of the concept, not a comprehensive
safety system. It will have false negatives. It was designed to be extended, but extension
requires manual rule authoring.

### 2. LLM-assisted analysis introduces LLM failure modes

When an adapter is provided, WorldSense delegates judgment to a language model. This reintroduces
the exact problems WorldSense is trying to solve:

- The LLM may produce overconfident risk assessments
- The LLM may hallucinate consequences that don't apply
- The LLM may be inconsistent across calls for the same input
- The LLM adds latency and cost

**The honest limit:** LLM-assisted mode is more powerful but less reliable than the rule
engine. "WorldSense + Claude" is not objectively safer than "Claude alone" — it adds a
second judgment pass, which may help or may compound errors.

### 3. Real-world coverage is shallow

The seed benchmark has 20 scenarios. The rule set covers approximately 15 explicit patterns.
Real-world risk is vastly more diverse. An agent operating in a production environment will
encounter situations that WorldSense has no rule for, at which point it returns `risk_level:
none` — which is not the same as "this is safe."

**The honest limit:** absence of a triggered rule is not a safety guarantee. Users must
understand that WorldSense reduces risk, it does not eliminate it.

### 4. The social reasoning module is rudimentary

The current `social.py` detects mentions of "boss", "manager", or "client" and applies a
generic professional tone recommendation. Real social risk is far more nuanced:

- Sarcasm, subtext, and implicit aggression in messages
- Cultural context that changes meaning
- Power dynamics beyond simple hierarchies
- Emotional states that affect interpretation

**The honest limit:** social reasoning in the current MVP is a placeholder. It flags the
right category but does not perform genuine social analysis.

### 5. Consequence simulation is template-based, not causal

The consequence simulator returns descriptions from YAML templates triggered by keywords.
It does not model causal chains, probability distributions, or interaction effects between
consequences. "Microsleep risk" is a string, not a probabilistic model.

**The honest limit:** consequence simulation is illustrative, not predictive. It is useful
for surfacing considerations a developer may have overlooked, not for making actuarial-grade
risk assessments.

---

## Parts that are overambitious in the current form

### The taxonomy has 21 categories but thin coverage per category

The taxonomy names 21 risk categories. The rule engine has meaningful coverage for perhaps
5-6 of them: `physical_safety`, `data_loss`, `workplace`, `travel_logistics`, `overconfidence`,
and `missing_context`. The other 15 categories may fire via the LLM adapter but have no
dedicated rules.

### The "social reasoning module" is a stub

`social.py` is 20 lines. The section heading in the architecture diagram implies a
sophisticated social model. The implementation is keyword detection. This gap is real.

### Multi-turn context is not implemented

The pipeline receives a single message. It has no memory of previous turns. Many real-world
risks are only detectable across a conversation — escalation, repeated risk-taking, evolving
context. This is a roadmap item, not a current feature.

---

## What to avoid claiming

**Do not claim:**
- "WorldSense makes AI safe." It reduces specific, detectable risks. Safety is a property of
  a whole system, not a single module.
- "WorldSense detects all risks." It detects risks it has rules or adapters for. Novel risks
  are invisible to it.
- "The risk level is accurate." It is an estimate based on limited signals. Treat it as a
  heuristic, not a measurement.
- "LLM-assisted mode is more reliable." It is more expressive. It may be less consistent.

**Do claim:**
- "WorldSense adds a practical judgment pass to LLM outputs."
- "WorldSense blocks or flags specific high-risk patterns reliably."
- "WorldSense makes risk reasoning inspectable and testable."
- "WorldSense is a starting point for building safer AI systems, not an endpoint."

---

## How not to seem like hype

The AI safety tooling space has a high ratio of impressive demos to actual utility. To avoid
this:

1. **Ship working code.** Rules that actually fire. Tests that actually pass. Benchmarks that
   actually measure something. ✅ Done.

2. **Be honest about the benchmark.** 20 scenarios is not a rigorous evaluation. State this
   explicitly. The benchmark exists to prevent regressions, not to prove the system works in
   all cases.

3. **Document false positives and false negatives.** Known failure modes are a feature, not
   a liability. A system with documented limits is more trustworthy than one that claims
   comprehensive coverage.

4. **Don't use the word "safe" without qualification.** Prefer "reduces the risk of" or
   "flags patterns associated with" over "prevents" or "ensures safety."

5. **Show the rules.** The YAML rule files are public. Anyone can read them and understand
   exactly what the system does and doesn't detect. This transparency is the project's
   strongest credibility signal.

---

## A smaller, more honest version of the idea

If the full vision feels too large, here is the minimum version that is genuinely useful:

**WorldSense as an action gate for coding agents.**

Focus exclusively on the `evaluate_action` function. Build a comprehensive, well-tested
rule set for filesystem operations, shell commands, database writes, API calls, and
network requests. Make the action gate the most reliable part of the system. Instrument
it with the MCP server so it works in Claude Code out of the box.

This is a narrower claim, but one that is fully deliverable and immediately useful for
anyone building an agentic coding assistant. Everything else in the roadmap is an expansion
of this foundation, not a prerequisite.

---

## Conclusion

WorldSense is a valid idea in an early, honest implementation. It solves a real problem —
LLMs lack practical judgment — but it solves a small, well-defined slice of it reliably
rather than claiming to solve the whole thing. That is the right trade-off for an open source
project at this stage.

The project earns credibility by being specific about what it does, transparent about how
it works, honest about its limits, and disciplined about not overpromising.
