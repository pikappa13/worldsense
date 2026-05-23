from worldsense import RealityEngine, RiskLevel


def test_driving_tired_is_high_risk() -> None:
    engine = RealityEngine()

    analysis = engine.analyze(
        user_message="Ho dormito 2 ore ma devo guidare 3 ore.",
        proposed_response="Bevi un caffe e parti.",
    )

    assert analysis.risk.risk_level == RiskLevel.HIGH
    assert "driving_fatigue" in analysis.triggered_rules
    assert analysis.rewrite_guidance is not None


def test_unknown_message_can_proceed() -> None:
    engine = RealityEngine()

    analysis = engine.analyze(user_message="Riassumi questo testo.")

    assert analysis.risk.risk_level == RiskLevel.NONE
    assert analysis.recommendations[0].action == "proceed"

