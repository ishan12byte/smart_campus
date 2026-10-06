"""M7.3 - Human Authorization Gateway.

This is the explicit human-in-the-loop boundary. It records authorization
without mutating incidents, priority, assignment, responsibility, or
escalation. A backend service can apply a separate, authenticated mutation
transaction after this authorization has been accepted.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional

from .decision_fusion import DecisionRecommendation
from .decision_validator import ValidationResult

APPROVE = "APPROVE"
MODIFY = "MODIFY"
REJECT = "REJECT"
DEFER = "DEFER"
VALID_AUTHORIZATION_ACTIONS = {APPROVE, MODIFY, REJECT, DEFER}

AUTHORIZED = "AUTHORIZED"
REJECTED = "REJECTED"
DEFERRED = "DEFERRED"


@dataclass(frozen=True)
class HumanAuthorization:
    """Immutable audit record of a human decision on an AI recommendation."""

    incident_id: str
    recommendation: str
    validation_allowed: bool
    action: str
    status: str
    reviewer_id: str
    reviewer_role: str
    reason: str
    final_action: str
    modified_fields: Dict[str, Any] = field(default_factory=dict)
    authorized_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class HumanAuthorizationGateway:
    """Authenticate/record the human authorization boundary."""

    def authorize(
        self,
        recommendation: DecisionRecommendation,
        validation: ValidationResult,
        reviewer_id: str,
        reviewer_role: str,
        action: str,
        reason: str,
        final_action: Optional[str] = None,
        modified_fields: Optional[Mapping[str, Any]] = None,
        authorized_at: Optional[datetime] = None,
    ) -> HumanAuthorization:
        if not isinstance(recommendation, DecisionRecommendation):
            raise TypeError("recommendation must be a DecisionRecommendation")
        if not isinstance(validation, ValidationResult):
            raise TypeError("validation must be a ValidationResult")
        if validation.incident_id != recommendation.incident_id:
            raise ValueError("recommendation and validation incident IDs must match")
        if not reviewer_id or not isinstance(reviewer_id, str):
            raise ValueError("reviewer_id is required")
        if not reviewer_role or not isinstance(reviewer_role, str):
            raise ValueError("reviewer_role is required")
        if action not in VALID_AUTHORIZATION_ACTIONS:
            raise ValueError(f"Invalid authorization action: {action}")
        if not reason or not reason.strip():
            raise ValueError("authorization reason is required")
        if not validation.allowed:
            raise ValueError("AI recommendation failed deterministic validation")

        modified = dict(modified_fields or {})

        if action == MODIFY and not modified:
            raise ValueError("MODIFY requires at least one modified field")

        if action != MODIFY and modified:
            raise ValueError("modified_fields are only valid for MODIFY")

        if final_action is None:
            if action == APPROVE:
                final_action = (
                    "KEEP_DETERMINISTIC_DECISION"
                    if recommendation.recommendation == "NO_RECOMMENDATION"
                    else "USE_VALIDATED_AI_RECOMMENDATION"
                )
            elif action == MODIFY:
                final_action = "APPLY_HUMAN_MODIFICATION"
            elif action == REJECT:
                final_action = "KEEP_DETERMINISTIC_DECISION"
            else:
                final_action = "DEFER_ACTION"

        if not isinstance(final_action, str) or not final_action.strip():
            raise ValueError("final_action is required")

        if authorized_at is None:
            authorized_at = datetime.now(timezone.utc)
        if not isinstance(authorized_at, datetime):
            raise TypeError("authorized_at must be a datetime")

        status = {
            APPROVE: AUTHORIZED,
            MODIFY: AUTHORIZED,
            REJECT: REJECTED,
            DEFER: DEFERRED,
        }[action]

        return HumanAuthorization(
            incident_id=recommendation.incident_id,
            recommendation=recommendation.recommendation,
            validation_allowed=validation.allowed,
            action=action,
            status=status,
            reviewer_id=reviewer_id,
            reviewer_role=reviewer_role,
            reason=reason.strip(),
            final_action=final_action.strip(),
            modified_fields=modified,
            authorized_at=authorized_at,
        )
