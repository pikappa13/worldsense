from worldsense import RealityEngine, RiskLevel


def test_delete_files_requires_confirmation_and_target() -> None:
    engine = RealityEngine()

    decision = engine.evaluate_action(
        {
            "tool": "filesystem.delete",
            "target": "/project/temp",
            "description": "Delete temporary files",
        },
        context={"user_confirmation": False},
    )

    assert decision.risk_level == RiskLevel.HIGH
    assert decision.requires_confirmation is True
    assert decision.should_block is True
    assert "user_confirmation" in decision.required_context
    assert "exact_target" not in decision.required_context


def test_delete_files_without_target_requires_exact_target() -> None:
    engine = RealityEngine()

    decision = engine.evaluate_action(
        {
            "tool": "filesystem.delete",
            "description": "Delete temporary files",
        },
        context={"user_confirmation": True},
    )

    assert decision.should_block is True
    assert "exact_target" in decision.required_context


def test_email_send_requires_review() -> None:
    engine = RealityEngine()

    decision = engine.evaluate_action(
        {"tool": "email.send", "description": "Send email to my boss"},
        context={"recipient": "boss@example.com"},
    )

    assert decision.risk_level == RiskLevel.MEDIUM
    assert decision.should_block is True
    assert "draft_reviewed" in decision.required_context
