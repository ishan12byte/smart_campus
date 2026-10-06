import pytest

from ai.components.evidence import (
    EvidenceCollector,
)
from ai.components.evidence_evaluator import (
    DUPLICATE_REVIEW,
    NO_ACTION,
    RECURRENCE_REVIEW,
    RESPONSIBILITY_REVIEW,
    EvidenceEvaluator,
)


def test_no_evidence_produces_no_action():
    collector = EvidenceCollector()

    collection = collector.collect("INC001")

    evaluator = EvidenceEvaluator()

    result = evaluator.evaluate(collection)

    assert result.signal == NO_ACTION
    assert result.confidence == 0.0
    assert result.evidence_count == 0
    assert len(result.limitations) == 1


def test_recurrence_produces_recurrence_review():
    collector = EvidenceCollector()

    collector.add_recurrence(
        incident_id="INC001",
        description="Three related incidents detected.",
        confidence=0.80,
    )

    collection = collector.collect("INC001")

    result = EvidenceEvaluator().evaluate(collection)

    assert result.signal == RECURRENCE_REVIEW
    assert result.confidence > 0.0
    assert result.evidence_count == 1


def test_related_incident_produces_duplicate_review():
    collector = EvidenceCollector()

    collector.add_related_incident(
        incident_id="INC001",
        related_incident_id="INC002",
        description="Strong semantic similarity.",
        confidence=0.85,
    )

    collection = collector.collect("INC001")

    result = EvidenceEvaluator().evaluate(collection)

    assert result.signal == DUPLICATE_REVIEW
    assert result.evidence_count == 1


def test_service_record_produces_responsibility_review():
    collector = EvidenceCollector()

    collector.add_service_record(
        incident_id="INC001",
        description="Cleaning recorded 20 minutes before incident.",
        confidence=1.0,
    )

    collection = collector.collect("INC001")

    result = EvidenceEvaluator().evaluate(collection)

    assert result.signal == RESPONSIBILITY_REVIEW


def test_recurrence_and_related_incident_produce_recurrence_review():
    collector = EvidenceCollector()

    collector.add_recurrence(
        incident_id="INC001",
        description="Four related incidents detected.",
        confidence=0.80,
    )

    collector.add_related_incident(
        incident_id="INC001",
        related_incident_id="INC002",
        description="Same projector issue.",
        confidence=0.85,
    )

    collection = collector.collect("INC001")

    result = EvidenceEvaluator().evaluate(collection)

    assert result.signal == RECURRENCE_REVIEW
    assert result.evidence_count == 2


def test_human_feedback_produces_responsibility_review():
    collector = EvidenceCollector()

    collector.add_human_feedback(
        incident_id="INC001",
        description="Reviewer marked as related event.",
        confidence=1.0,
        metadata={
            "outcome": "RELATED_EVENT",
            "reviewer_id": "staff_001",
        },
    )

    collection = collector.collect("INC001")

    result = EvidenceEvaluator().evaluate(collection)

    assert result.signal == RESPONSIBILITY_REVIEW


def test_image_evidence_does_not_assign_responsibility():
    collector = EvidenceCollector()

    collector.add_image_evidence(
        incident_id="INC001",
        description="Image shows visible equipment damage.",
        confidence=0.75,
    )

    collection = collector.collect("INC001")

    result = EvidenceEvaluator().evaluate(collection)

    assert result.signal == NO_ACTION
    assert any(
        "does not establish responsibility"
        in limitation
        for limitation in result.limitations
    )


def test_service_record_has_limitation():
    collector = EvidenceCollector()

    collector.add_service_record(
        incident_id="INC001",
        description="Cleaning record exists.",
    )

    collection = collector.collect("INC001")

    result = EvidenceEvaluator().evaluate(collection)

    assert any(
        "does not by itself prove service effectiveness"
        in limitation
        for limitation in result.limitations
    )


def test_human_feedback_has_limitation():
    collector = EvidenceCollector()

    collector.add_human_feedback(
        incident_id="INC001",
        description="Reviewer confirmed related event.",
    )

    collection = collector.collect("INC001")

    result = EvidenceEvaluator().evaluate(collection)

    assert any(
        "Human feedback is recorded evidence"
        in limitation
        for limitation in result.limitations
    )


def test_confidence_never_exceeds_one():
    collector = EvidenceCollector()

    for _ in range(10):
        collector.add_recurrence(
            incident_id="INC001",
            description="Recurring pattern.",
            confidence=1.0,
        )

    collection = collector.collect("INC001")

    result = EvidenceEvaluator().evaluate(collection)

    assert 0.0 <= result.confidence <= 1.0
    assert result.confidence == 1.0


def test_evidence_summary_contains_supporting_evidence():
    collector = EvidenceCollector()

    collector.add_recurrence(
        incident_id="INC001",
        description="Recurring pattern detected.",
        confidence=0.80,
    )

    collector.add_service_record(
        incident_id="INC001",
        description="Recent service record.",
        confidence=1.0,
    )

    collection = collector.collect("INC001")

    result = EvidenceEvaluator().evaluate(collection)

    assert len(result.supporting_evidence) >= 2


def test_invalid_collection_type_is_rejected():
    evaluator = EvidenceEvaluator()

    with pytest.raises(TypeError):
        evaluator.evaluate("not an evidence collection")