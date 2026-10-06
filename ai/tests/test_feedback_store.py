import pytest

from ai.components.feedback_store import FeedbackStore
from ai.components.human_review import (
    HumanReviewService,
    CONFIRM_DUPLICATE,
    RELATED_EVENT,
    SEPARATE_INCIDENT,
)


def create_review(
    incident_id="INC001",
    candidate_id="INC002",
    ai_decision="LIKELY_DUPLICATE",
    ai_score=0.6615,
    outcome=CONFIRM_DUPLICATE,
    reviewer_id="staff_001",
    reason="Same projector issue in the same room.",
):
    service = HumanReviewService()

    return service.review(
        incident_id=incident_id,
        candidate_incident_id=candidate_id,
        ai_decision=ai_decision,
        ai_score=ai_score,
        outcome=outcome,
        reviewer_id=reviewer_id,
        reviewer_reason=reason,
    )


def test_review_is_recorded():
    store = FeedbackStore()

    review = create_review()

    record = store.record_review(review)

    assert record.incident_id == "INC001"
    assert record.candidate_incident_id == "INC002"
    assert record.ai_decision == "LIKELY_DUPLICATE"
    assert record.ai_score == 0.6615
    assert record.human_outcome == CONFIRM_DUPLICATE
    assert record.reviewer_id == "staff_001"
    assert record.reviewer_reason == (
        "Same projector issue in the same room."
    )


def test_recorded_timestamp_exists():
    store = FeedbackStore()

    record = store.record_review(create_review())

    assert record.recorded_at is not None


def test_multiple_reviews_are_stored():
    store = FeedbackStore()

    review_1 = create_review(
        incident_id="INC001",
        candidate_id="INC002",
        outcome=CONFIRM_DUPLICATE,
    )

    review_2 = create_review(
        incident_id="INC001",
        candidate_id="INC003",
        ai_decision="REVIEW",
        ai_score=0.6710,
        outcome=RELATED_EVENT,
        reason="Different rooms but potentially related event.",
    )

    store.record_review(review_1)
    store.record_review(review_2)

    assert store.count() == 2
    assert len(store.get_all()) == 2


def test_get_for_incident_returns_related_feedback():
    store = FeedbackStore()

    store.record_review(
        create_review(
            incident_id="INC001",
            candidate_id="INC002",
        )
    )

    store.record_review(
        create_review(
            incident_id="INC003",
            candidate_id="INC004",
            ai_decision="REVIEW",
            ai_score=0.55,
            outcome=SEPARATE_INCIDENT,
        )
    )

    results = store.get_for_incident("INC001")

    assert len(results) == 1
    assert results[0].incident_id == "INC001"


def test_candidate_incident_is_also_searchable():
    store = FeedbackStore()

    store.record_review(
        create_review(
            incident_id="INC001",
            candidate_id="INC002",
        )
    )

    results = store.get_for_incident("INC002")

    assert len(results) == 1
    assert results[0].candidate_incident_id == "INC002"


def test_unknown_incident_returns_empty_list():
    store = FeedbackStore()

    store.record_review(create_review())

    results = store.get_for_incident("INC999")

    assert results == []


def test_get_all_returns_copy():
    store = FeedbackStore()

    store.record_review(create_review())

    records = store.get_all()
    records.clear()

    assert store.count() == 1


def test_invalid_review_type_is_rejected():
    store = FeedbackStore()

    with pytest.raises(TypeError):
        store.record_review("not a review")