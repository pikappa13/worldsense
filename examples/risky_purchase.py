from worldsense import RealityEngine


engine = RealityEngine()
analysis = engine.analyze(
    user_message="Comprami il portatile migliore, anche se e' costoso.",
    proposed_response="Prendo il primo modello top di gamma.",
)

print(analysis.model_dump_json(indent=2))

