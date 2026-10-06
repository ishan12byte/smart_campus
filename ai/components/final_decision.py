"""M7.4 - Final Decision and audit contract."""

from dataclasses import asdict, dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, Optional

from decision_engine.engine import DecisionResult

from .decision_fusion import DecisionRecommendation
from .decision_validator import ValidationResult
from .human_authorization import (
    AUTHORIZED,
    DEFERRED,
    REJECTED,
    HumanAuthorization,
)

FINAL_PENDING_AUTHORIZATION = "PENDING_AUTHORIZATION"
FINAL_AUTHORIZED = "AUTHORIZED"
FINAL_REJECTED = "REJECTED"
FINAL_DEFERRED = "DEFERRED"


@dataclass(frozen=True)
class FinalDecisionAudit:
    orchestrator_version: str
    policy_version: str
    generated_at: datetime


@dataclass(frozen=True)
class FinalDecision:
    """Single backend-facing contract for the end-to-end decision path."""

    incident_id: str
    deterministic_decision: DecisionResult
    ai_recommendation: DecisionRecommendation
    validation: ValidationResult
    human_authorization: Optional[HumanAuthorization]
    final_status: str
    final_action: str
    confidence: float
    audit: FinalDecisionAudit

    @property
    def human_authorized(self) -> bool:
        return self.final_status == FINAL_AUTHORIZED

    def to_dict(self) -> dict[str, Any]:
        return _jsonable(asdict(self))


def build_final_decision(
    deterministic_decision: DecisionResult,
    ai_recommendation: DecisionRecommendation,
    validation: ValidationResult,
    human_authorization: Optional[HumanAuthorization] = None,
    *,
    orchestrator_version: str = "1.0.0",
    policy_version: str = "1.0.0",
    generated_at: Optional[datetime] = None,
) -> FinalDecision:
    incident_id = ai_recommendation.incident_id

    if deterministic_decision.incident.id <= 0:
        raise ValueError("deterministic decision has an invalid incident ID")
    if validation.incident_id != incident_id:
        raise ValueError("validation incident_id must match AI recommendation")
    if human_authorization is not None:
        if human_authorization.incident_id != incident_id:
            raise ValueError("human authorization incident_id must match")
        if not validation.allowed:
            raise ValueError("cannot authorize a recommendation that failed validation")

    if human_authorization is None:
        final_status = FINAL_PENDING_AUTHORIZATION
        final_action = "PENDING_HUMAN_AUTHORIZATION"
    elif human_authorization.status == AUTHORIZED:
        final_status = FINAL_AUTHORIZED
        final_action = human_authorization.final_action
    elif human_authorization.status == REJECTED:
        final_status = FINAL_REJECTED
        final_action = "KEEP_DETERMINISTIC_DECISION"
    elif human_authorization.status == DEFERRED:
        final_status = FINAL_DEFERRED
        final_action = "DEFER_ACTION"
    else:
        raise ValueError(
            f"Unsupported authorization status: {human_authorization.status}"
        )

    if generated_at is None:
        generated_at = datetime.now().astimezone()

    audit = FinalDecisionAudit(
        orchestrator_version=orchestrator_version,
        policy_version=policy_version,
        generated_at=generated_at,
    )

    return FinalDecision(
        incident_id=incident_id,
        deterministic_decision=deterministic_decision,
        ai_recommendation=ai_recommendation,
        validation=validation,
        human_authorization=human_authorization,
        final_status=final_status,
        final_action=final_action,
        confidence=ai_recommendation.confidence,
        audit=audit,
    )


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value
