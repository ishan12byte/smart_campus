"""
M7.1 - Decision Fusion

Combines deterministic decision information with AI evidence.

Important boundary:

AI can recommend.
Deterministic policy validates.
Human authorization remains authoritative.

This component does NOT:
- assign blame automatically
- change priority automatically
- merge incidents automatically
- assign departments automatically
- escalate emergencies automatically
- call external emergency services
"""

from dataclasses import dataclass
from typing import Optional, Tuple

from .evidence_fusion import (
    FusedEvidenceResult,
    FUSION_NO_ACTION,
    FUSION_REVIEW,
    FUSION_SUPPORTING,
)


# ---------------------------------------------------------------------------
# Recommendation types
# ---------------------------------------------------------------------------

NO_RECOMMENDATION = "NO_RECOMMENDATION"

REVIEW_DUPLICATE = "REVIEW_DUPLICATE"
REVIEW_RECURRENCE = "REVIEW_RECURRENCE"
REVIEW_RESPONSIBILITY = "REVIEW_RESPONSIBILITY"
REVIEW_EVIDENCE = "REVIEW_EVIDENCE"

SUPPORTING_EVIDENCE = "SUPPORTING_EVIDENCE"


VALID_RECOMMENDATIONS = {
    NO_RECOMMENDATION,
    REVIEW_DUPLICATE,
    REVIEW_RECURRENCE,
    REVIEW_RESPONSIBILITY,
    REVIEW_EVIDENCE,
    SUPPORTING_EVIDENCE,
}


@dataclass(frozen=True)
class DecisionContext:
    """
    Existing deterministic decision information.

    These values are treated as authoritative inputs to the fusion layer.
    """

    priority: Optional[str] = None
    responsibility_status: Optional[str] = None
    assigned_department: Optional[str] = None
    escalation_level: Optional[str] = None


@dataclass(frozen=True)
class DecisionRecommendation:
    """
    AI-assisted recommendation.

    This is NOT the final campus decision.
    """

    incident_id: str

    recommendation: str

    confidence: float

    reason: str

    evidence_signals: Tuple[str, ...]

    supporting_evidence: Tuple[str, ...]

    limitations: Tuple[str, ...]

    human_review_required: bool

    deterministic_priority: Optional[str]

    deterministic_responsibility: Optional[str]

    deterministic_department: Optional[str]

    deterministic_escalation: Optional[str]


class DecisionFusion:
    """
    Fuse AI evidence with an existing deterministic decision context.

    The deterministic context is never overwritten by this component.
    """

    def fuse(
        self,
        incident_id: str,
        evidence: FusedEvidenceResult,
        deterministic: DecisionContext,
    ) -> DecisionRecommendation:

        if not incident_id:
            raise ValueError("incident_id must not be empty")

        if not isinstance(evidence, FusedEvidenceResult):
            raise TypeError(
                "evidence must be a FusedEvidenceResult"
            )

        if evidence.incident_id != incident_id:
            raise ValueError(
                "evidence incident_id must match incident_id"
            )

        if not isinstance(deterministic, DecisionContext):
            raise TypeError(
                "deterministic must be a DecisionContext"
            )

        recommendation, reason = self._determine_recommendation(
            evidence
        )

        return DecisionRecommendation(
            incident_id=incident_id,
            recommendation=recommendation,
            confidence=evidence.confidence,
            reason=reason,
            evidence_signals=evidence.signals,
            supporting_evidence=evidence.supporting_evidence,
            limitations=evidence.limitations,
            human_review_required=evidence.human_review_required,
            deterministic_priority=deterministic.priority,
            deterministic_responsibility=(
                deterministic.responsibility_status
            ),
            deterministic_department=(
                deterministic.assigned_department
            ),
            deterministic_escalation=(
                deterministic.escalation_level
            ),
        )

    @staticmethod
    def _determine_recommendation(
        evidence: FusedEvidenceResult,
    ) -> Tuple[str, str]:

        signals = set(evidence.signals)

        # Duplicate review has the highest interpretation priority
        # because merging incidents is potentially destructive.
        if "DUPLICATE_REVIEW" in signals:
            return (
                REVIEW_DUPLICATE,
                (
                    "Evidence indicates a possible duplicate or related "
                    "incident. Human review is required before any merge "
                    "or consolidation."
                ),
            )

        if "RECURRENCE_REVIEW" in signals:
            return (
                REVIEW_RECURRENCE,
                (
                    "Evidence indicates a recurring incident pattern. "
                    "The pattern should be reviewed without treating "
                    "recurrence as an increase in incident severity."
                ),
            )

        if "RESPONSIBILITY_REVIEW" in signals:
            return (
                REVIEW_RESPONSIBILITY,
                (
                    "Evidence relevant to responsibility was identified. "
                    "Human authorization is required before changing "
                    "responsibility status."
                ),
            )

        if evidence.status == FUSION_REVIEW:
            return (
                REVIEW_EVIDENCE,
                (
                    "Evidence requires human interpretation before "
                    "downstream action."
                ),
            )

        if evidence.status == FUSION_SUPPORTING:
            return (
                SUPPORTING_EVIDENCE,
                (
                    "Supporting evidence is available but does not "
                    "produce an actionable AI recommendation."
                ),
            )

        return (
            NO_RECOMMENDATION,
            (
                "No actionable AI evidence was identified. "
                "The deterministic decision remains unchanged."
            ),
        )