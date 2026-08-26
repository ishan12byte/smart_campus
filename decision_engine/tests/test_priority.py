from decision_engine.priority import calculate_priority


def test_low_priority():
    result = calculate_priority(
        impact=1,
        urgency=1,
        safety=1,
        deadline=1,
        recurrence=1,
    )

    assert result["level"] == "LOW"


def test_high_priority():
    result = calculate_priority(
        impact=5,
        urgency=5,
        safety=1,
        deadline=5,
        recurrence=2,
    )

    assert result["level"] == "HIGH"


def test_critical_exam_issue():
    result = calculate_priority(
        impact=5,
        urgency=5,
        safety=3,
        deadline=5,
        recurrence=4,
    )

    assert result["level"] == "CRITICAL"


def test_fire_override():
    result = calculate_priority(
        impact=1,
        urgency=1,
        safety=1,
        deadline=1,
        recurrence=1,
        incident_type="FIRE",
    )

    assert result["level"] == "CRITICAL"


def test_invalid_score():
    try:
        calculate_priority(
            impact=6,
            urgency=1,
            safety=1,
            deadline=1,
            recurrence=1,
        )
        assert False
    except ValueError:
        assert True
