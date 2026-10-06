"""M7.2 - Deterministic Decision Validator.

The validator is a policy/safety boundary between an AI recommendation and
human authorization. It never turns an AI recommendation into an executable
operational action by itself.
"""

from dataclasses import dataclass
from typing import Tuple

from .decision_fusion import (
    DecisionRecommendation,
    NO_RECOMMENDATION,
    REVIEW_DUPLICATE,
    REVIEW_RECURRENCE,
    REVIEW_RESPONSIBILITY,
    REVIEW_EVIDENCE,
    SUPPORTING_EVIDENCE,
)

VALID_RECOMMENDATIONS = {
    NO_RECOMMENDATION,
    REVIEW_DUPLICATE,
    REVIEW_RECURRENCE,
    REVIEW_RESPONSIBILITY,
    REVIEW_EVIDENCE,
    SUPPORTING_EVIDENCE,
}

CRITICAL = "CRITICAL"
HIGH = "HIGH"
MEDIUM = "MEDIUM"
LOW = "LOW"
VALID_PRIORITIES = {CRITICAL, HIGH, MEDIUM, LOW}


@dataclass(frozen=True)
class ValidationResult:
    """Deterministic validation result; still not a final decision."""

    incident_id: str
    recommendation: str
    allowed: bool
    confidence: float
    reasons: Tuple[str, ...]
    warnings: Tuple[str, ...]
    human_authorization_required: bool
    priority_protected: bool
    responsibility_protected: bool
    escalation_protected: bool


class DecisionValidator:
    """Validate AI recommendations against campus safety constraints."""

    def validate(
        self,
        recommendation: DecisionRecommendation,
    ) -> ValidationResult:
        if not isinstance(recommendation, DecisionRecommendation):
            raise TypeError("recommendation must be a DecisionRecommendation")
        if not recommendation.incident_id:
            raise ValueError("recommendation incident_id must not be empty")
        if recommendation.recommendation not in VALID_RECOMMENDATIONS:
            raise ValueError("invalid recommendation type")
        if not 0.0 <= recommendation.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        priority = recommendation.deterministic_priority
        if priority is not None and priority not in VALID_PRIORITIES:
            raise ValueError("invalid deterministic priority")

        reasons = [
            "AI recommendation is advisory only.",
            "Deterministic campus decisions remain protected.",
        ]
        warnings = []

        if priority == CRITICAL:
            warnings.append(
                "CRITICAL priority is protected and cannot be downgraded by AI evidence."
            )

        if recommendation.recommendation == REVIEW_DUPLICATE:
            reasons.append(
                "Potential duplicate incidents require human review before merge or consolidation."
            )
            warnings.append("No automatic incident merge is permitted.")

        if recommendation.recommendation == REVIEW_RECURRENCE:
            reasons.append(
                "Recurrence may be surfaced for review but does not automatically increase severity."
            )
            warnings.append("Recurrence cannot independently change priority.")

        if recommendation.recommendation == REVIEW_RESPONSIBILITY:
            reasons.append(
                "Responsibility-related evidence requires human authorization."
            )
            warnings.append(
                "AI cannot automatically assign blame or department responsibility."
            )

        if recommendation.recommendation == REVIEW_EVIDENCE:
            reasons.append(
                "Evidence requires human interpretation before operational action."
            )

        if recommendation.recommendation == SUPPORTING_EVIDENCE:
            reasons.append(
                "Supporting evidence does not independently authorize an operational action."
            )

        if recommendation.recommendation == NO_RECOMMENDATION:
            reasons.append(
                "No actionable AI recommendation was produced."
            )

        if recommendation.deterministic_responsibility is not None:
            warnings.append(
                "Existing responsibility status is protected from automatic AI replacement."
            )

        if recommendation.deterministic_department is not None:
            warnings.append(
                "Existing department assignment is protected from automatic AI replacement."
            )

        if recommendation.deterministic_escalation is not None:
            warnings.append(
                "Existing escalation level is protected from automatic AI removal or downgrade."
            )

        review_recommendations = {
            REVIEW_DUPLICATE,
            REVIEW_RECURRENCE,
            REVIEW_RESPONSIBILITY,
            REVIEW_EVIDENCE,
        }
        human_required = (
            recommendation.human_review_required
            or recommendation.recommendation in review_recommendations
        )

        # Every currently supported recommendation is allowed to exist as an
        # advisory result. "allowed" does not mean "executable".
        return ValidationResult(
            incident_id=recommendation.incident_id,
            recommendation=recommendation.recommendation,
            allowed=True,
            confidence=recommendation.confidence,
            reasons=tuple(reasons),
            warnings=tuple(warnings),
            human_authorization_required=human_required,
            priority_protected=True,
            responsibility_protected=True,
            escalation_protected=True,
        )
