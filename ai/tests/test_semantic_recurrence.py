import pytest

from ai.components.semantic_recurrence import (
    NO_RECURRENCE,
    RECURRENCE_DETECTED,
    REVIEW_RECURRING_PATTERN,
    SemanticRecurrenceAnalyzer,
)


class FakeMatcher:
    def __init__(self, candidates):
        self.candidates = candidates

    def predict(self, data):
        from ai.schemas import AIResult

        return AIResult(
            candidates=tuple(self.candidates),
            recommendations=(),
            model_name="fake",
            model_version="1.0",
            fallback_used=False,
        )


class FakeCandidate:
    def __init__(self, incident_id, score):
        self.incident_id = incident_id
        self.score = score


def make_incident(
    incident_id,
    location="Academic Block A, Room 204",
    category="IT",
    subcategory="PROJECTOR",
    service_cycle_id="PROJ-R204-2026-09",
    reported_at="2026-09-15T10:00:00",
):
    return {
        "incident_id": incident_id,
        "description": "Projector issue",
        "category": category,
        "subcategory": subcategory,
        "location": location,
        "service_cycle_id": service_cycle_id,
        "reported_at": reported_at,
    }


def test_recurrence_is_detected():
    matcher = FakeMatcher(
        [
            FakeCandidate("INC001", 0.80),
            FakeCandidate("INC002", 0.75),
        ]
    )

    analyzer = SemanticRecurrenceAnalyzer(
        matcher=matcher,
        semantic_threshold=0.50,
        recurrence_threshold=0.55,
        minimum_occurrences=3,
    )

    query = make_incident("INC003")

    history = [
        make_incident("INC001"),
        make_incident("INC002"),
    ]

    result = analyzer.analyze(
        query,
        history,
    )

    assert result.status == RECURRENCE_DETECTED
    assert result.occurrence_count == 3
    assert result.matching_incident_ids == (
        "INC001",
        "INC002",
    )


def test_insufficient_candidates_do_not_trigger_recurrence():
    matcher = FakeMatcher(
        [
            FakeCandidate("INC001", 0.80),
        ]
    )

    analyzer = SemanticRecurrenceAnalyzer(
        matcher=matcher,
        minimum_occurrences=3,
    )

    query = make_incident("INC002")

    history = [
        make_incident("INC001"),
    ]

    result = analyzer.analyze(
        query,
        history,
    )

    assert result.status == NO_RECURRENCE
    assert result.occurrence_count == 2


def test_different_location_requires_review():
    matcher = FakeMatcher(
        [
            FakeCandidate("INC001", 0.80),
            FakeCandidate("INC002", 0.75),
        ]
    )

    analyzer = SemanticRecurrenceAnalyzer(
        matcher=matcher,
        minimum_occurrences=3,
    )

    query = make_incident(
        "INC003",
        location="Academic Block A, Room 204",
    )

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

    result = analyzer.analyze(
        query,
        history,
    )

    assert result.status == REVIEW_RECURRING_PATTERN
    assert result.occurrence_count == 3


def test_different_category_is_filtered():
    matcher = FakeMatcher(
        [
            FakeCandidate("INC001", 0.90),
        ]
    )

    analyzer = SemanticRecurrenceAnalyzer(
        matcher=matcher,
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

    result = analyzer.analyze(
        query,
        history,
    )

    assert result.status == NO_RECURRENCE
    assert result.occurrence_count == 1


def test_old_candidate_is_filtered():
    matcher = FakeMatcher(
        [
            FakeCandidate("INC001", 0.90),
        ]
    )

    analyzer = SemanticRecurrenceAnalyzer(
        matcher=matcher,
        minimum_occurrences=2,
        top_k=10,
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

    result = analyzer.analyze(
        query,
        history,
        time_window_days=30,
    )

    assert result.status == NO_RECURRENCE
    assert result.occurrence_count == 1


def test_candidates_are_ranked_by_context_score():
    matcher = FakeMatcher(
        [
            FakeCandidate("INC001", 0.70),
            FakeCandidate("INC002", 0.90),
        ]
    )

    analyzer = SemanticRecurrenceAnalyzer(
        matcher=matcher,
        minimum_occurrences=2,
    )

    query = make_incident("INC003")

    history = [
        make_incident("INC001"),
        make_incident("INC002"),
    ]

    result = analyzer.analyze(
        query,
        history,
    )

    assert len(result.candidates) == 2

    assert (
        result.candidates[0].context_score
        >= result.candidates[1].context_score
    )


def test_query_incident_is_excluded():
    matcher = FakeMatcher(
        [
            FakeCandidate("INC001", 0.90),
            FakeCandidate("INC002", 0.80),
        ]
    )

    analyzer = SemanticRecurrenceAnalyzer(
        matcher=matcher,
        minimum_occurrences=2,
    )

    query = make_incident("INC001")

    history = [
        query,
        make_incident("INC002"),
    ]

    result = analyzer.analyze(
        query,
        history,
    )

    assert "INC001" not in result.matching_incident_ids


def test_invalid_threshold_is_rejected():
    with pytest.raises(ValueError):
        SemanticRecurrenceAnalyzer(
            semantic_threshold=1.5,
        )


def test_invalid_recurrence_threshold_is_rejected():
    with pytest.raises(ValueError):
        SemanticRecurrenceAnalyzer(
            recurrence_threshold=-0.1,
        )


def test_invalid_minimum_occurrences_is_rejected():
    with pytest.raises(ValueError):
        SemanticRecurrenceAnalyzer(
            minimum_occurrences=1,
        )


def test_invalid_top_k_is_rejected():
    with pytest.raises(ValueError):
        SemanticRecurrenceAnalyzer(
            top_k=0,
        )


def test_missing_query_id_is_rejected():
    analyzer = SemanticRecurrenceAnalyzer(
        matcher=FakeMatcher([]),
    )

    with pytest.raises(ValueError):
        analyzer.analyze(
            {},
            [],
        )