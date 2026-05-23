from worldsense.validation import validate_project


def test_project_validation_passes() -> None:
    report = validate_project()

    assert report.passed is True
    assert report.issues == []
