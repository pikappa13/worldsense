from worldsense import RealityEngine, RiskLevel


def test_impossible_trip_flags_constraint() -> None:
    engine = RealityEngine()

    analysis = engine.analyze(
        user_message="Voglio visitare Roma, Firenze, Venezia, Milano e Napoli in un giorno.",
        proposed_response="Si puo fare partendo presto.",
    )

    assert analysis.risk.risk_level == RiskLevel.HIGH
    assert analysis.constraint_violations
    assert analysis.constraint_violations[0].constraint_type == "travel_logistics"


def test_overconfident_current_claim_flags_uncertainty() -> None:
    engine = RealityEngine()

    analysis = engine.analyze(
        user_message="Dimmi sicuramente qual e' il prezzo attuale migliore.",
        proposed_response="Sicuramente e' questo.",
    )

    assert analysis.uncertainty_assessment is not None
    assert analysis.uncertainty_assessment.unsupported_claims
    assert analysis.uncertainty_assessment.should_search_external_sources is True

