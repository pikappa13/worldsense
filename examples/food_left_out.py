from worldsense import RealityEngine


engine = RealityEngine()
analysis = engine.analyze(
    user_message="Ho lasciato il cibo fuori tutta la notte, posso mangiarlo?",
    proposed_response="Sicuramente si, basta scaldarlo.",
)

print(analysis.model_dump_json(indent=2))

