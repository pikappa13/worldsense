from worldsense import RealityEngine


engine = RealityEngine()
analysis = engine.analyze(
    user_message="Dimmi sicuramente qual e' il prezzo attuale migliore.",
    proposed_response="Sicuramente e' questo, non serve verificare.",
)

print(analysis.model_dump_json(indent=2))

