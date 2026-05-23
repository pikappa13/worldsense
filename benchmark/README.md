# WorldSense Benchmark

The benchmark measures whether WorldSense catches risks that fluent LLM answers often miss.

## Scenario Categories

- travel realism
- destructive actions
- social escalation
- missing context
- medical or physical risk
- overconfident claims
- irreversible decisions
- tool-use safety
- time feasibility
- emotional impulsivity

## Metrics

- risk detection accuracy
- missing context detection
- consequence coverage
- false positives
- false negatives
- action blocking correctness
- recommendation usefulness
- developer usability

## Dataset

The seed dataset is `data/seed_scenarios.jsonl`. Each row includes expected risk level, expected
categories, expected missing information, and expected action.

