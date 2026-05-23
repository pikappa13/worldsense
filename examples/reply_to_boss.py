from worldsense import RealityEngine


engine = RealityEngine()
analysis = engine.analyze(
    user_message="Rispondi a questa mail del mio capo.",
    proposed_response="Digli che non e' colpa tua e che doveva spiegarsi meglio.",
)

print(analysis.model_dump_json(indent=2))

