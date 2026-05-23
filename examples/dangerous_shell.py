from worldsense import RealityEngine


engine = RealityEngine()
decision = engine.evaluate_action(
    action={"tool": "shell.run", "description": "rm -rf /tmp/build"},
    context={"command_reviewed": False},
)

print(decision.model_dump_json(indent=2))

