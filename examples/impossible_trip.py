from worldsense import RealityEngine


engine = RealityEngine()
analysis = engine.analyze(
    user_message="Voglio visitare Roma, Firenze, Venezia, Milano e Napoli in un giorno.",
    proposed_response="Si puo fare se parti molto presto.",
)

print(analysis.model_dump_json(indent=2))

