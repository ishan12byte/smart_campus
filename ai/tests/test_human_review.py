import pytest

from ai.components.human_review import (
    HumanReviewService,
    CONFIRM_DUPLICATE,
    RELATED_EVENT,
    SEPARATE_INCIDENT,
    FALSE_MATCH,
)


def test_confirm_duplicate_review():
    service = HumanReviewService()

    result = service.review(
        incident_id="INC001",
        candidate_incident_id="INC002",
        ai_decision="LIKELY_DUPLICATE",
        ai_score=0.6615,
        outcome=CONFIRM_DUPLICATE,
        reviewer_id="staff_001",
        reviewer_reason="Same projector issue in the same room.",
    )

    assert result.incident_id == "INC001"
    assert result.candidate_incident_id == "INC002"
    assert result.outcome == CONFIRM_DUPLICATE
    assert result.reviewer_id == "staff_001"


def test_related_event_review():
    service = HumanReviewService()

    result = service.review(
        incident_id="INC001",
        candidate_incident_id="INC003",
        ai_decision="REVIEW",
        ai_score=0.6710,
        outcome=RELATED_EVENT,
        reviewer_id="staff_001",
    )

    assert result.outcome == RELATED_EVENT


def test_separate_incident_review():
    service = HumanReviewService()

    result = service.review(
        incident_id="INC001",
        candidate_incident_id="INC003",
        ai_decision="REVIEW",
        ai_score=0.6710,
        outcome=SEPARATE_INCIDENT,
        reviewer_id="staff_001",
    )

    assert result.outcome == SEPARATE_INCIDENT


def test_false_match_review():
    service = HumanReviewService()

    result = service.review(
        incident_id="INC001",
        candidate_incident_id="INC019",
        ai_decision="NO_MATCH",
        ai_score=0.2471,
        outcome=FALSE_MATCH,
        reviewer_id="staff_001",
    )

    assert result.outcome == FALSE_MATCH


def test_same_incident_is_rejected():
    service = HumanReviewService()

    with pytest.raises(ValueError):
        service.review(
            incident_id="INC001",
            candidate_incident_id="INC001",
            ai_decision="LIKELY_DUPLICATE",
            ai_score=0.8,
            outcome=CONFIRM_DUPLICATE,
            reviewer_id="staff_001",
        )


def test_invalid_score_is_rejected():
    service = HumanReviewService()

    with pytest.raises(ValueError):
        service.review(
            incident_id="INC001",
            candidate_incident_id="INC002",
            ai_decision="LIKELY_DUPLICATE",
            ai_score=1.5,
            outcome=CONFIRM_DUPLICATE,
            reviewer_id="staff_001",
        )


def test_invalid_outcome_is_rejected():
    service = HumanReviewService()

    with pytest.raises(ValueError):
        service.review(
            incident_id="INC001",
            candidate_incident_id="INC002",
            ai_decision="REVIEW",
            ai_score=0.6,
            outcome="AUTO_MERGE",
            reviewer_id="staff_001",
        )


def test_missing_reviewer_is_rejected():
    service = HumanReviewService()

    with pytest.raises(ValueError):
        service.review(
            incident_id="INC001",
            candidate_incident_id="INC002",
            ai_decision="REVIEW",
            ai_score=0.6,
            outcome=RELATED_EVENT,
            reviewer_id="",
        )