import pytest

from ai.components.evidence import (
    INCIDENT_DESCRIPTION,
    IMAGE_EVIDENCE,
    HUMAN_FEEDBACK,
    RECURRENCE_PATTERN,
    RELATED_INCIDENT,
    SERVICE_RECORD,
    EvidenceCollector,
    EvidenceItem,
)


def test_add_evidence_item():
    collector = EvidenceCollector()

    item = EvidenceItem(
        evidence_type=INCIDENT_DESCRIPTION,
        source="incident_report",
        description="Projector displays a black screen.",
        confidence=1.0,
        incident_id="INC001",
    )

    result = collector.add(item)

    assert result == item


def test_collect_empty_evidence():
    collector = EvidenceCollector()

    result = collector.collect("INC001")

    assert result.incident_id == "INC001"
    assert result.evidence_count == 0
    assert result.items == ()
    assert result.has_image_evidence is False
    assert result.has_human_feedback is False
    assert result.has_recurrence_evidence is False
    assert result.has_service_evidence is False


def test_incident_description_helper():
    collector = EvidenceCollector()

    collector.add_incident_description(
        incident_id="INC001",
        description="Projector is not displaying an image.",
    )

    result = collector.collect("INC001")

    assert result.evidence_count == 1
    assert result.items[0].evidence_type == INCIDENT_DESCRIPTION


def test_related_incident_helper():
    collector = EvidenceCollector()

    collector.add_related_incident(
        incident_id="INC001",
        related_incident_id="INC002",
        description="Similar projector issue in the same room.",
        confidence=0.82,
    )

    result = collector.collect("INC001")

    assert result.evidence_count == 1
    assert result.items[0].evidence_type == RELATED_INCIDENT
    assert result.items[0].confidence == 0.82
    assert result.items[0].incident_id == "INC002"


def test_recurrence_helper():
    collector = EvidenceCollector()

    collector.add_recurrence(
        incident_id="INC001",
        description="Three related incidents detected.",
        confidence=0.76,
        metadata={
            "occurrence_count": 3,
        },
    )

    result = collector.collect("INC001")

    assert result.has_recurrence_evidence is True
    assert result.items[0].metadata["occurrence_count"] == 3


def test_service_record_helper():
    collector = EvidenceCollector()

    collector.add_service_record(
        incident_id="INC001",
        description="Cleaning recorded 20 minutes before report.",
    )

    result = collector.collect("INC001")

    assert result.has_service_evidence is True
    assert result.items[0].evidence_type == SERVICE_RECORD


def test_human_feedback_helper():
    collector = EvidenceCollector()

    collector.add_human_feedback(
        incident_id="INC001",
        description="Reviewer confirmed related incident.",
        metadata={
            "outcome": "RELATED_EVENT",
            "reviewer_id": "staff_001",
        },
    )

    result = collector.collect("INC001")

    assert result.has_human_feedback is True
    assert result.items[0].evidence_type == HUMAN_FEEDBACK


def test_image_evidence_helper():
    collector = EvidenceCollector()

    collector.add_image_evidence(
        incident_id="INC001",
        description="Uploaded image shows visible projector damage.",
        confidence=0.70,
    )

    result = collector.collect("INC001")

    assert result.has_image_evidence is True
    assert result.items[0].evidence_type == IMAGE_EVIDENCE


def test_all_evidence_flags():
    collector = EvidenceCollector()

    collector.add_incident_description(
        "INC001",
        "Projector is not working.",
    )

    collector.add_related_incident(
        "INC001",
        "INC002",
        "Similar projector incident.",
        0.80,
    )

    collector.add_recurrence(
        "INC001",
        "Three related incidents found.",
        0.75,
    )

    collector.add_service_record(
        "INC001",
        "Service record found.",
    )

    collector.add_human_feedback(
        "INC001",
        "Human reviewer confirmed related event.",
    )

    collector.add_image_evidence(
        "INC001",
        "Image evidence available.",
    )

    result = collector.collect("INC001")

    assert result.evidence_count == 6
    assert result.has_image_evidence is True
    assert result.has_human_feedback is True
    assert result.has_recurrence_evidence is True
    assert result.has_service_evidence is True


def test_invalid_evidence_type_is_rejected():
    collector = EvidenceCollector()

    item = EvidenceItem(
        evidence_type="INVALID",
        source="test",
        description="Invalid evidence.",
    )

    with pytest.raises(ValueError):
        collector.add(item)


def test_invalid_confidence_is_rejected():
    collector = EvidenceCollector()

    item = EvidenceItem(
        evidence_type=INCIDENT_DESCRIPTION,
        source="test",
        description="Invalid confidence.",
        confidence=1.5,
    )

    with pytest.raises(ValueError):
        collector.add(item)


def test_missing_source_is_rejected():
    collector = EvidenceCollector()

    item = EvidenceItem(
        evidence_type=INCIDENT_DESCRIPTION,
        source="",
        description="Missing source.",
    )

    with pytest.raises(ValueError):
        collector.add(item)


def test_missing_description_is_rejected():
    collector = EvidenceCollector()

    item = EvidenceItem(
        evidence_type=INCIDENT_DESCRIPTION,
        source="incident_report",
        description="",
    )

    with pytest.raises(ValueError):
        collector.add(item)


def test_missing_incident_id_is_rejected():
    collector = EvidenceCollector()

    with pytest.raises(ValueError):
        collector.collect("")