from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

from ai.components.human_review import ReviewDecision


@dataclass(frozen=True)
class FeedbackRecord:
    incident_id: str
    candidate_incident_id: str
    ai_decision: str
    ai_score: float
    human_outcome: str
    reviewer_id: str
    reviewer_reason: Optional[str]
    recorded_at: datetime


class FeedbackStore:
    """
    Storage-independent feedback collection layer.

    Human review decisions are stored as immutable feedback records.
    This component does not modify incidents or AI decisions.
    """

    def __init__(self):
        self._records: List[FeedbackRecord] = []

    def record_review(
        self,
        review: ReviewDecision,
    ) -> FeedbackRecord:

        if not isinstance(review, ReviewDecision):
            raise TypeError(
                "review must be a ReviewDecision"
            )

        record = FeedbackRecord(
            incident_id=review.incident_id,
            candidate_incident_id=review.candidate_incident_id,
            ai_decision=review.ai_decision,
            ai_score=review.ai_score,
            human_outcome=review.outcome,
            reviewer_id=review.reviewer_id,
            reviewer_reason=review.reviewer_reason,
            recorded_at=datetime.now(timezone.utc),
        )

        self._records.append(record)

        return record

    def get_all(self) -> List[FeedbackRecord]:
        return list(self._records)

    def get_for_incident(
        self,
        incident_id: str,
    ) -> List[FeedbackRecord]:

        return [
            record
            for record in self._records
            if record.incident_id == incident_id
            or record.candidate_incident_id == incident_id
        ]

    def count(self) -> int:
        return len(self._records)

    def clear(self) -> None:
        self._records.clear()