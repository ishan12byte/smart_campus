from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# Evidence source types
INCIDENT_DESCRIPTION = "INCIDENT_DESCRIPTION"
RELATED_INCIDENT = "RELATED_INCIDENT"
RECURRENCE_PATTERN = "RECURRENCE_PATTERN"
SERVICE_RECORD = "SERVICE_RECORD"
HUMAN_FEEDBACK = "HUMAN_FEEDBACK"
LOCATION_CONTEXT = "LOCATION_CONTEXT"
IMAGE_EVIDENCE = "IMAGE_EVIDENCE"


VALID_EVIDENCE_TYPES = {
    INCIDENT_DESCRIPTION,
    RELATED_INCIDENT,
    RECURRENCE_PATTERN,
    SERVICE_RECORD,
    HUMAN_FEEDBACK,
    LOCATION_CONTEXT,
    IMAGE_EVIDENCE,
}


@dataclass(frozen=True)
class EvidenceItem:
    """
    A single piece of structured evidence.

    Evidence is descriptive. It does not itself determine
    responsibility, priority, assignment, or escalation.
    """

    evidence_type: str
    source: str
    description: str
    confidence: float = 1.0
    incident_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvidenceCollection:
    """
    Collection of evidence associated with an incident.
    """

    incident_id: str
    items: Tuple[EvidenceItem, ...]
    evidence_count: int
    has_image_evidence: bool
    has_human_feedback: bool
    has_recurrence_evidence: bool
    has_service_evidence: bool


class EvidenceCollector:
    """
    Collects and validates structured evidence.

    This component does not make decisions. It only gathers
    evidence from already available intelligence signals.
    """

    def __init__(self):
        self._items: List[EvidenceItem] = []

    @staticmethod
    def _validate_item(item: EvidenceItem) -> None:

        if not isinstance(item, EvidenceItem):
            raise TypeError(
                "item must be an EvidenceItem"
            )

        if item.evidence_type not in VALID_EVIDENCE_TYPES:
            raise ValueError(
                f"Invalid evidence type: {item.evidence_type}"
            )

        if not item.source:
            raise ValueError(
                "Evidence source is required"
            )

        if not item.description:
            raise ValueError(
                "Evidence description is required"
            )

        if not 0.0 <= item.confidence <= 1.0:
            raise ValueError(
                "Evidence confidence must be between 0 and 1"
            )

    def add(self, item: EvidenceItem) -> EvidenceItem:
        """
        Add one validated evidence item.
        """

        self._validate_item(item)

        self._items.append(item)

        return item

    def add_incident_description(
        self,
        incident_id: str,
        description: str,
    ) -> EvidenceItem:

        item = EvidenceItem(
            evidence_type=INCIDENT_DESCRIPTION,
            source="incident_report",
            description=description,
            confidence=1.0,
            incident_id=incident_id,
        )

        return self.add(item)

    def add_related_incident(
        self,
        incident_id: str,
        related_incident_id: str,
        description: str,
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EvidenceItem:

        item = EvidenceItem(
            evidence_type=RELATED_INCIDENT,
            source="semantic_matching",
            description=description,
            confidence=confidence,
            incident_id=related_incident_id,
            metadata=metadata or {},
        )

        return self.add(item)

    def add_recurrence(
        self,
        incident_id: str,
        description: str,
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EvidenceItem:

        item = EvidenceItem(
            evidence_type=RECURRENCE_PATTERN,
            source="recurrence_analyzer",
            description=description,
            confidence=confidence,
            incident_id=incident_id,
            metadata=metadata or {},
        )

        return self.add(item)

    def add_service_record(
        self,
        incident_id: str,
        description: str,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EvidenceItem:

        item = EvidenceItem(
            evidence_type=SERVICE_RECORD,
            source="service_records",
            description=description,
            confidence=confidence,
            incident_id=incident_id,
            metadata=metadata or {},
        )

        return self.add(item)

    def add_human_feedback(
        self,
        incident_id: str,
        description: str,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EvidenceItem:

        item = EvidenceItem(
            evidence_type=HUMAN_FEEDBACK,
            source="human_review",
            description=description,
            confidence=confidence,
            incident_id=incident_id,
            metadata=metadata or {},
        )

        return self.add(item)

    def add_image_evidence(
        self,
        incident_id: str,
        description: str,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EvidenceItem:

        item = EvidenceItem(
            evidence_type=IMAGE_EVIDENCE,
            source="incident_attachment",
            description=description,
            confidence=confidence,
            incident_id=incident_id,
            metadata=metadata or {},
        )

        return self.add(item)

    def collect(
        self,
        incident_id: str,
    ) -> EvidenceCollection:

        if not incident_id:
            raise ValueError(
                "incident_id is required"
            )

        items = tuple(self._items)

        return EvidenceCollection(
            incident_id=incident_id,
            items=items,
            evidence_count=len(items),
            has_image_evidence=any(
                item.evidence_type == IMAGE_EVIDENCE
                for item in items
            ),
            has_human_feedback=any(
                item.evidence_type == HUMAN_FEEDBACK
                for item in items
            ),
            has_recurrence_evidence=any(
                item.evidence_type == RECURRENCE_PATTERN
                for item in items
            ),
            has_service_evidence=any(
                item.evidence_type == SERVICE_RECORD
                for item in items
            ),
        )

    def clear(self) -> None:
        self._items.clear()