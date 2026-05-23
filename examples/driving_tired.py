from worldsense import RealityEngine


engine = RealityEngine()
analysis = engine.analyze(
    user_message="Ho dormito 2 ore ma devo guidare 3 ore.",
    proposed_response="Fai delle pause e bevi un caffe.",
)

print(analysis.model_dump_json(indent=2))

