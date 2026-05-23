from worldsense import RealityEngine


engine = RealityEngine()
decision = engine.evaluate_action(
    action={"tool": "email.send", "recipient": "boss@example.com"},
    context={"draft_reviewed": False},
)

print(decision.model_dump_json(indent=2))

