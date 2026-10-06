from dataclasses import dataclass
from typing import List, Tuple

from ai.components.evidence import (
    EvidenceCollection,
    EvidenceItem,
    IMAGE_EVIDENCE,
    HUMAN_FEEDBACK,
    RECURRENCE_PATTERN,
    RELATED_INCIDENT,
    SERVICE_RECORD,
)


NO_ACTION = "NO_ACTION"
RESPONSIBILITY_REVIEW = "RESPONSIBILITY_REVIEW"
RECURRENCE_REVIEW = "RECURRENCE_REVIEW"
DUPLICATE_REVIEW = "DUPLICATE_REVIEW"


VALID_SIGNALS = {
    NO_ACTION,
    RESPONSIBILITY_REVIEW,
    RECURRENCE_REVIEW,
    DUPLICATE_REVIEW,
}


@dataclass(frozen=True)
class EvidenceAssessment:
    incident_id: str
    signal: str
    confidence: float
    supporting_evidence: Tuple[str, ...]
    limitations: Tuple[str, ...]
    evidence_count: int


class EvidenceEvaluator:
    """
    Evaluates collected evidence and produces an explainable signal.

    This component does NOT:
    - assign responsibility
    - change priority
    - assign a department
    - escalate an incident
    - merge incidents

    It only interprets the available evidence and reports
    supporting evidence and limitations.
    """

    def evaluate(
        self,
        collection: EvidenceCollection,
    ) -> EvidenceAssessment:

        if not isinstance(collection, EvidenceCollection):
            raise TypeError(
                "collection must be an EvidenceCollection"
            )

        items = collection.items

        if not items:
            return EvidenceAssessment(
                incident_id=collection.incident_id,
                signal=NO_ACTION,
                confidence=0.0,
                supporting_evidence=(),
                limitations=(
                    "No supporting evidence is currently available.",
                ),
                evidence_count=0,
            )

        recurrence_items = self._items_of_type(
            items,
            RECURRENCE_PATTERN,
        )

        related_items = self._items_of_type(
            items,
            RELATED_INCIDENT,
        )

        service_items = self._items_of_type(
            items,
            SERVICE_RECORD,
        )

        human_items = self._items_of_type(
            items,
            HUMAN_FEEDBACK,
        )

        image_items = self._items_of_type(
            items,
            IMAGE_EVIDENCE,
        )

        supporting = []
        limitations = []

        if recurrence_items:
            supporting.append(
                "Recurring incident pattern detected."
            )

        if related_items:
            supporting.append(
                "Related historical incidents were identified."
            )

        if service_items:
            supporting.append(
                "Relevant service-record evidence is available."
            )

        if human_items:
            supporting.append(
                "Human review feedback is available."
            )

        if image_items:
            supporting.append(
                "Image evidence is available as supporting evidence."
            )

        # Human feedback is evidence, but not automatically treated
        # as absolute truth by this evaluator.
        if human_items:
            limitations.append(
                "Human feedback is recorded evidence and should "
                "be interpreted according to the review outcome."
            )

        # Image evidence is deliberately limited.
        if image_items:
            limitations.append(
                "Image evidence alone does not establish "
                "responsibility or causation."
            )

        # A service record proves that a service event was recorded,
        # not necessarily that the service was effective.
        if service_items:
            limitations.append(
                "A service record confirms recorded service activity "
                "but does not by itself prove service effectiveness."
            )

        if not supporting:
            limitations.append(
                "Available evidence does not currently support "
                "a specific intelligence signal."
            )

        signal = self._determine_signal(
            recurrence_items=recurrence_items,
            related_items=related_items,
            service_items=service_items,
            human_items=human_items,
        )

        confidence = self._calculate_confidence(
            items=items,
            recurrence_items=recurrence_items,
            related_items=related_items,
            service_items=service_items,
            human_items=human_items,
        )

        return EvidenceAssessment(
            incident_id=collection.incident_id,
            signal=signal,
            confidence=confidence,
            supporting_evidence=tuple(supporting),
            limitations=tuple(limitations),
            evidence_count=len(items),
        )

    @staticmethod
    def _items_of_type(
        items: Tuple[EvidenceItem, ...],
        evidence_type: str,
    ) -> List[EvidenceItem]:

        return [
            item
            for item in items
            if item.evidence_type == evidence_type
        ]

    @staticmethod
    def _determine_signal(
        recurrence_items: List[EvidenceItem],
        related_items: List[EvidenceItem],
        service_items: List[EvidenceItem],
        human_items: List[EvidenceItem],
    ) -> str:

        # Strong recurrence + related incidents indicates that
        # recurrence should be reviewed.
        if recurrence_items and related_items:
            return RECURRENCE_REVIEW

        # Recurrence alone is sufficient to flag a recurring pattern.
        if recurrence_items:
            return RECURRENCE_REVIEW

        # Related incidents can support duplicate investigation.
        if related_items:
            return DUPLICATE_REVIEW

        # Service evidence without recurrence/related incidents
        # should not automatically imply responsibility.
        if service_items:
            return RESPONSIBILITY_REVIEW

        # Human feedback without another evidence category is
        # preserved but should not independently trigger blame.
        if human_items:
            return RESPONSIBILITY_REVIEW

        return NO_ACTION

    @staticmethod
    def _calculate_confidence(
        items: Tuple[EvidenceItem, ...],
        recurrence_items: List[EvidenceItem],
        related_items: List[EvidenceItem],
        service_items: List[EvidenceItem],
        human_items: List[EvidenceItem],
    ) -> float:

        if not items:
            return 0.0

        # Use evidence confidence as the foundation.
        average_confidence = sum(
            item.confidence
            for item in items
        ) / len(items)

        bonus = 0.0

        if recurrence_items:
            bonus += 0.10

        if related_items:
            bonus += 0.05

        if service_items:
            bonus += 0.05

        if human_items:
            bonus += 0.05

        confidence = min(
            1.0,
            average_confidence + bonus,
        )

        return round(confidence, 4)