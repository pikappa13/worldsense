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

print(decision.model_dump_json(indent=2))

