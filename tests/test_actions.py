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


def test_database_drop_is_critical() -> None:
    engine = RealityEngine()

    decision = engine.evaluate_action(
        {"tool": "database.query", "description": "DROP TABLE users"},
        context={"command_reviewed": True},
    )

    assert decision.risk_level == RiskLevel.CRITICAL
    assert decision.should_block is True
    assert "backup_available" in decision.required_context


def test_shell_run_prefers_shell_rule_over_file_keyword_rule() -> None:
    engine = RealityEngine()

    decision = engine.evaluate_action(
        {"tool": "shell.run", "description": "rm -rf /tmp/build"},
        context={"command_reviewed": False},
    )

    assert decision.side_effect_type == "destructive_or_security_sensitive"
    assert "command_reviewed" in decision.required_context
