"""
M6.3 - Evidence Fusion

Combines EvidenceCollection and EvidenceAssessment objects into a single,
auditable evidence result.

Design principles:
- Evidence fusion does NOT make final responsibility decisions.
- Evidence fusion does NOT change incident priority.
- Evidence fusion does NOT automatically merge incidents.
- Human decisions remain authoritative.
- Image evidence is supporting evidence only.
- Service records show recorded activity, not effectiveness.
- Recurrence indicates a pattern, not severity.
"""

from dataclasses import dataclass
from typing import Tuple

from .evidence import EvidenceCollection, EvidenceItem
from .evidence_evaluator import (
    EvidenceAssessment,
    NO_ACTION,
    RESPONSIBILITY_REVIEW,
    RECURRENCE_REVIEW,
    DUPLICATE_REVIEW,
)


FUSION_NO_ACTION = "NO_ACTION"
FUSION_REVIEW = "REVIEW"
FUSION_SUPPORTING = "SUPPORTING_EVIDENCE"


@dataclass(frozen=True)
class FusedEvidenceResult:
    """Final fused representation of evidence for one incident."""

    incident_id: str

    # High-level fusion outcome
    status: str

    # Signals discovered by EvidenceEvaluator
    signals: Tuple[str, ...]

    # All evidence contributing to the fusion
    evidence: Tuple[EvidenceItem, ...]

    # Human-readable supporting evidence
    supporting_evidence: Tuple[str, ...]

    # Important limitations/caveats
    limitations: Tuple[str, ...]

    # Number of evidence items
    evidence_count: int

    # Number of evaluator assessments
    assessment_count: int

    # Aggregated confidence
    confidence: float

    # Whether a human should review the fused evidence
    human_review_required: bool


class EvidenceFusion:
    """
    Deterministically fuses evidence assessments and evidence items.

    This class intentionally does not make downstream decisions such as:
    - responsibility assignment
    - priority assignment
    - incident merging
    - department assignment
    """

    VALID_ASSESSMENT_SIGNALS = {
        NO_ACTION,
        RESPONSIBILITY_REVIEW,
        RECURRENCE_REVIEW,
        DUPLICATE_REVIEW,
    }

    def fuse(
        self,
        collection: EvidenceCollection,
        assessments: Tuple[EvidenceAssessment, ...],
    ) -> FusedEvidenceResult:
        """Fuse evidence collection and evaluator assessments."""

        if not isinstance(collection, EvidenceCollection):
            raise TypeError("collection must be an EvidenceCollection")

        if not isinstance(assessments, tuple):
            raise TypeError("assessments must be a tuple")

        for assessment in assessments:
            if not isinstance(assessment, EvidenceAssessment):
                raise TypeError(
                    "all assessments must be EvidenceAssessment instances"
                )

            if assessment.incident_id != collection.incident_id:
                raise ValueError(
                    "assessment incident_id must match collection incident_id"
                )

            if assessment.signal not in self.VALID_ASSESSMENT_SIGNALS:
                raise ValueError(
                    f"invalid assessment signal: {assessment.signal}"
                )

            if not 0.0 <= assessment.confidence <= 1.0:
                raise ValueError(
                    "assessment confidence must be between 0 and 1"
                )

        evidence = collection.items

        signals = self._extract_signals(assessments)

        supporting_evidence = self._merge_supporting_evidence(
            assessments
        )

        limitations = self._merge_limitations(assessments)

        confidence = self._calculate_confidence(
            assessments=assessments,
            evidence_count=len(evidence),
        )

        status = self._determine_status(
            signals=signals,
            evidence_count=len(evidence),
        )

        human_review_required = self._requires_human_review(
            signals=signals
        )

        return FusedEvidenceResult(
            incident_id=collection.incident_id,
            status=status,
            signals=signals,
            evidence=evidence,
            supporting_evidence=supporting_evidence,
            limitations=limitations,
            evidence_count=len(evidence),
            assessment_count=len(assessments),
            confidence=confidence,
            human_review_required=human_review_required,
        )

    @staticmethod
    def _extract_signals(
        assessments: Tuple[EvidenceAssessment, ...],
    ) -> Tuple[str, ...]:
        """Extract unique actionable signals in stable order."""

        ordered_signals = []

        for assessment in assessments:
            signal = assessment.signal

            if signal == NO_ACTION:
                continue

            if signal not in ordered_signals:
                ordered_signals.append(signal)

        return tuple(ordered_signals)

    @staticmethod
    def _merge_supporting_evidence(
        assessments: Tuple[EvidenceAssessment, ...],
    ) -> Tuple[str, ...]:
        """Combine evaluator evidence summaries without duplicates."""

        result = []

        for assessment in assessments:
            for item in assessment.supporting_evidence:
                if item not in result:
                    result.append(item)

        return tuple(result)

    @staticmethod
    def _merge_limitations(
        assessments: Tuple[EvidenceAssessment, ...],
    ) -> Tuple[str, ...]:
        """Combine evaluator limitations without duplicates."""

        result = []

        for assessment in assessments:
            for limitation in assessment.limitations:
                if limitation not in result:
                    result.append(limitation)

        return tuple(result)

    @staticmethod
    def _calculate_confidence(
        assessments: Tuple[EvidenceAssessment, ...],
        evidence_count: int,
    ) -> float:
        """
        Calculate conservative aggregate confidence.

        With assessments:
            average confidence

        With evidence but no assessments:
            low confidence because the evidence has not been evaluated.

        With no evidence:
            0.0
        """

        if evidence_count == 0:
            return 0.0

        if not assessments:
            return 0.0

        average = sum(
            assessment.confidence
            for assessment in assessments
        ) / len(assessments)

        return round(min(max(average, 0.0), 1.0), 4)

    @staticmethod
    def _determine_status(
        signals: Tuple[str, ...],
        evidence_count: int,
    ) -> str:
        """
        Determine the overall evidence status.

        Priority:
            review signals > supporting evidence > no action
        """

        if any(
            signal in {
                RESPONSIBILITY_REVIEW,
                RECURRENCE_REVIEW,
                DUPLICATE_REVIEW,
            }
            for signal in signals
        ):
            return FUSION_REVIEW

        if evidence_count > 0:
            return FUSION_SUPPORTING

        return FUSION_NO_ACTION

    @staticmethod
    def _requires_human_review(
        signals: Tuple[str, ...],
    ) -> bool:
        """
        Evidence requiring interpretation is surfaced for human review.

        The fusion layer never performs the human decision itself.
        """

        review_signals = {
            RESPONSIBILITY_REVIEW,
            RECURRENCE_REVIEW,
            DUPLICATE_REVIEW,
        }

        return any(signal in review_signals for signal in signals)