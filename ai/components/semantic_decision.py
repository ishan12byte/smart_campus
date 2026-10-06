from dataclasses import dataclass


@dataclass(frozen=True)
class SemanticDecision:
    decision: str
    score: float
    reason: str


class SemanticDecisionEngine:
    """
    Converts semantic similarity into an explainable recommendation.

    This component does not:
    - merge incidents
    - delete incidents
    - determine responsibility
    - assign departments
    - modify incident priority

    It only provides a semantic similarity recommendation.
    """

    NO_MATCH = "NO_MATCH"
    REVIEW = "REVIEW"
    LIKELY_DUPLICATE = "LIKELY_DUPLICATE"

    def __init__(
        self,
        review_threshold: float = 0.40,
        duplicate_threshold: float = 0.50,
    ):
        if not 0.0 <= review_threshold <= 1.0:
            raise ValueError(
                "review_threshold must be between 0 and 1"
            )

        if not 0.0 <= duplicate_threshold <= 1.0:
            raise ValueError(
                "duplicate_threshold must be between 0 and 1"
            )

        if review_threshold > duplicate_threshold:
            raise ValueError(
                "review_threshold cannot exceed duplicate_threshold"
            )

        self.review_threshold = review_threshold
        self.duplicate_threshold = duplicate_threshold

    def decide(self, score: float) -> SemanticDecision:
        if not 0.0 <= score <= 1.0:
            raise ValueError(
                "similarity score must be between 0 and 1"
            )

        if score >= self.duplicate_threshold:
            return SemanticDecision(
                decision=self.LIKELY_DUPLICATE,
                score=score,
                reason=(
                    "Semantic similarity exceeds the "
                    "duplicate recommendation threshold."
                ),
            )

        if score >= self.review_threshold:
            return SemanticDecision(
                decision=self.REVIEW,
                score=score,
                reason=(
                    "Semantic similarity is significant "
                    "but requires human review."
                ),
            )

        return SemanticDecision(
            decision=self.NO_MATCH,
            score=score,
            reason=(
                "Semantic similarity is below the "
                "review threshold."
            ),
        )