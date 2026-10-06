from dataclasses import dataclass
from typing import Optional


CONFIRM_DUPLICATE = "CONFIRM_DUPLICATE"
RELATED_EVENT = "RELATED_EVENT"
SEPARATE_INCIDENT = "SEPARATE_INCIDENT"
FALSE_MATCH = "FALSE_MATCH"


VALID_OUTCOMES = {
    CONFIRM_DUPLICATE,
    RELATED_EVENT,
    SEPARATE_INCIDENT,
    FALSE_MATCH,
}


@dataclass(frozen=True)
class ReviewDecision:
    incident_id: str
    candidate_incident_id: str
    ai_decision: str
    ai_score: float
    outcome: str
    reviewer_id: str
    reviewer_reason: Optional[str] = None


class HumanReviewService:
    """
    Records human decisions on AI-generated incident candidate matches.

    The human decision is authoritative. This component does not
    automatically merge, delete, reassign, or modify incidents.
    """

    def review(
        self,
        incident_id: str,
        candidate_incident_id: str,
        ai_decision: str,
        ai_score: float,
        outcome: str,
        reviewer_id: str,
        reviewer_reason: Optional[str] = None,
    ) -> ReviewDecision:

        if not incident_id:
            raise ValueError("incident_id is required")

        if not candidate_incident_id:
            raise ValueError("candidate_incident_id is required")

        if incident_id == candidate_incident_id:
            raise ValueError(
                "incident_id and candidate_incident_id must be different"
            )

        if not isinstance(ai_score, (int, float)):
            raise ValueError("ai_score must be numeric")

        if not 0.0 <= float(ai_score) <= 1.0:
            raise ValueError("ai_score must be between 0 and 1")

        if outcome not in VALID_OUTCOMES:
            raise ValueError(
                f"Invalid review outcome: {outcome}"
            )

        if not reviewer_id:
            raise ValueError("reviewer_id is required")

        return ReviewDecision(
            incident_id=incident_id,
            candidate_incident_id=candidate_incident_id,
            ai_decision=ai_decision,
            ai_score=float(ai_score),
            outcome=outcome,
            reviewer_id=reviewer_id,
            reviewer_reason=reviewer_reason,
        )