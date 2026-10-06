import pytest

from ai.components.recurrence_analyzer import (
    NO_RECURRENCE,
    RECURRENCE_DETECTED,
    RecurrenceAnalyzer,
)


def make_incident(
    incident_id,
    reported_at="2026-09-15T10:00:00",
    category="IT",
    subcategory="PROJECTOR",
    location="Academic Block A, Room 204",
    service_cycle_id="PROJ-R204-2026-09",
):
    return {
        "incident_id": incident_id,
        "description": "Projector issue",
        "reported_at": reported_at,
        "category": category,
        "subcategory": subcategory,
        "location": location,
        "service_cycle_id": service_cycle_id,
    }


def test_recurrence_is_detected():
    analyzer = RecurrenceAnalyzer(
        minimum_occurrences=3,
        time_window_days=30,
    )

    query = make_incident(
        "INC004",
        "2026-09-20T10:00:00",
    )

    history = [
        make_incident(
            "INC001",
            "2026-09-01T10:00:00",
        ),
        make_incident(
            "INC002",
            "2026-09-05T10:00:00",
        ),
        make_incident(
            "INC003",
            "2026-09-10T10:00:00",
        ),
    ]

    result = analyzer.analyze(query, history)

    assert result.status == RECURRENCE_DETECTED
    assert result.occurrence_count == 4
    assert result.matching_incident_ids == (
        "INC001",
        "INC002",
        "INC003",
    )


def test_recurrence_threshold_counts_query_incident():
    """
    minimum_occurrences represents total occurrences,
    including the current query incident.

    Therefore:
        2 historical matches + 1 query = 3 total
    """

    analyzer = RecurrenceAnalyzer(
        minimum_occurrences=3,
    )

    query = make_incident("INC003")

    history = [
        make_incident("INC001"),
        make_incident("INC002"),
    ]

    result = analyzer.analyze(query, history)

    assert result.status == RECURRENCE_DETECTED
    assert result.occurrence_count == 3
    assert result.matching_incident_ids == (
        "INC001",
        "INC002",
    )


def test_no_recurrence_when_below_threshold():
    """
    One historical match + current query = 2 total.
    With minimum_occurrences=3, recurrence should not be detected.
    """

    analyzer = RecurrenceAnalyzer(
        minimum_occurrences=3,
    )

    query = make_incident("INC002")

    history = [
        make_incident("INC001"),
    ]

    result = analyzer.analyze(query, history)

    assert result.status == NO_RECURRENCE
    assert result.occurrence_count == 2
    assert result.matching_incident_ids == ("INC001",)


def test_different_location_does_not_match():
    analyzer = RecurrenceAnalyzer(
        minimum_occurrences=3,
    )

    query = make_incident("INC003")

    history = [
        make_incident(
            "INC001",
            location="Academic Block A, Room 204",
        ),
        make_incident(
            "INC002",
            location="Academic Block B, Room 310",
        ),
    ]

    result = analyzer.analyze(query, history)

    assert result.status == NO_RECURRENCE

    # Query itself + one matching historical incident.
    assert result.occurrence_count == 2

    assert result.matching_incident_ids == (
        "INC001",
    )


def test_different_category_does_not_match():
    analyzer = RecurrenceAnalyzer(
        minimum_occurrences=2,
    )

    query = make_incident("INC002")

    history = [
        make_incident(
            "INC001",
            category="MAINTENANCE",
            subcategory="ELECTRICAL",
        ),
    ]

    result = analyzer.analyze(query, history)

    assert result.status == NO_RECURRENCE
    assert result.occurrence_count == 1
    assert result.matching_incident_ids == ()


def test_service_cycle_difference_does_not_match():
    analyzer = RecurrenceAnalyzer(
        minimum_occurrences=2,
    )

    query = make_incident(
        "INC002",
        service_cycle_id="PROJ-R204-2026-10",
    )

    history = [
        make_incident(
            "INC001",
            service_cycle_id="PROJ-R204-2026-09",
        ),
    ]

    result = analyzer.analyze(query, history)

    assert result.status == NO_RECURRENCE
    assert result.occurrence_count == 1
    assert result.matching_incident_ids == ()


def test_old_incidents_outside_window_are_ignored():
    analyzer = RecurrenceAnalyzer(
        minimum_occurrences=2,
        time_window_days=30,
    )

    query = make_incident(
        "INC002",
        reported_at="2026-10-01T10:00:00",
    )

    history = [
        make_incident(
            "INC001",
            reported_at="2026-08-01T10:00:00",
        ),
    ]

    result = analyzer.analyze(query, history)

    assert result.status == NO_RECURRENCE
    assert result.occurrence_count == 1
    assert result.matching_incident_ids == ()


def test_query_incident_is_excluded():
    analyzer = RecurrenceAnalyzer(
        minimum_occurrences=2,
    )

    query = make_incident("INC001")

    history = [
        query,
        make_incident("INC002"),
    ]

    result = analyzer.analyze(query, history)

    assert result.matching_incident_ids == (
        "INC002",
    )

    assert result.occurrence_count == 2


def test_invalid_minimum_occurrences():
    with pytest.raises(ValueError):
        RecurrenceAnalyzer(
            minimum_occurrences=1,
        )


def test_invalid_time_window():
    with pytest.raises(ValueError):
        RecurrenceAnalyzer(
            time_window_days=0,
        )


def test_missing_query_id():
    analyzer = RecurrenceAnalyzer()

    with pytest.raises(ValueError):
        analyzer.analyze(
            {},
            [],
        )