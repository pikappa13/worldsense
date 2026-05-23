from worldsense import RealityEngine


engine = RealityEngine()
analysis = engine.analyze(
    user_message="Voglio licenziarmi oggi.",
    proposed_response="Se lo senti, fallo subito.",
)

print(analysis.model_dump_json(indent=2))

