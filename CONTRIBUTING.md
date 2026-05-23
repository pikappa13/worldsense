# Contributing

WorldSense is early alpha. Contributions should keep the project practical, inspectable, and useful
without paid APIs.

Good first contributions:

- new YAML rules with tests
- benchmark scenarios
- clearer consequence templates
- action safety policies
- adapter examples
- documentation improvements

Rules for contributions:

- Add tests for behavior changes.
- Prefer explicit structured outputs over vague prose.
- Do not add mandatory paid API dependencies.
- Avoid claims that WorldSense guarantees safety or replaces expert judgment.
- Keep rule IDs stable once released.

Run checks before opening a pull request:

```bash
python -m pytest
python -m ruff check .
```

