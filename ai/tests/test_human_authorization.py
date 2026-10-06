from datetime import datetime, timezone
import pytest

from ai.components.decision_fusion import DecisionRecommendation, NO_RECOMMENDATION, REVIEW_DUPLICATE
from ai.components.decision_validator import DecisionValidator
from ai.components.human_authorization import (
    APPROVE, MODIFY, REJECT, DEFER,
    AUTHORIZED, REJECTED, DEFERRED,
    HumanAuthorization,
    HumanAuthorizationGateway,
)


def rec(recommendation=REVIEW_DUPLICATE):
    return DecisionRecommendation(
        incident_id="INC001",
        recommendation=recommendation,
        confidence=0.9,
        reason="test",
        evidence_signals=("DUPLICATE_REVIEW",) if recommendation != NO_RECOMMENDATION else (),
        supporting_evidence=(),
        limitations=(),
        human_review_required=recommendation != NO_RECOMMENDATION,
        deterministic_priority="HIGH",
        deterministic_responsibility="PENDING_REVIEW",
        deterministic_department="IT",
        deterministic_escalation="NONE",
    )


def validated(r):
    return DecisionValidator().validate(r)


def test_approve_creates_authorized_record():
    fixed = datetime(2026, 10, 6, tzinfo=timezone.utc)
    result = HumanAuthorizationGateway().authorize(
        recommendation=rec(),
        validation=validated(rec()),
        reviewer_id="staff-1",
        reviewer_role="DEPARTMENT_HEAD",
        action=APPROVE,
        reason="Reviewed evidence and approved the recommendation.",
        authorized_at=fixed,
    )
    assert isinstance(result, HumanAuthorization)
    assert result.status == AUTHORIZED
    assert result.final_action == "USE_VALIDATED_AI_RECOMMENDATION"
    assert result.authorized_at == fixed


def test_modify_requires_explicit_modified_fields():
    gateway = HumanAuthorizationGateway()
    with pytest.raises(ValueError):
        gateway.authorize(
            recommendation=rec(), validation=validated(rec()), reviewer_id="s",
            reviewer_role="SUPER_ADMIN", action=MODIFY, reason="change"
        )

    result = gateway.authorize(
        recommendation=rec(), validation=validated(rec()), reviewer_id="s",
        reviewer_role="SUPER_ADMIN", action=MODIFY, reason="Human change",
        modified_fields={"review_note": "Keep as separate event"},
    )
    assert result.status == AUTHORIZED
    assert result.modified_fields["review_note"] == "Keep as separate event"


def test_reject_and_defer_do_not_execute_ai_action():
    gateway = HumanAuthorizationGateway()
    for action, expected in [(REJECT, REJECTED), (DEFER, DEFERRED)]:
        result = gateway.authorize(
            recommendation=rec(), validation=validated(rec()), reviewer_id="s",
            reviewer_role="SUPER_ADMIN", action=action, reason="Not ready"
        )
        assert result.status == expected


def test_no_recommendation_can_be_explicitly_approved_as_deterministic():
    recommendation = rec(NO_RECOMMENDATION)
    result = HumanAuthorizationGateway().authorize(
        recommendation=recommendation,
        validation=validated(recommendation),
        reviewer_id="s",
        reviewer_role="DEPARTMENT_HEAD",
        action=APPROVE,
        reason="Continue with deterministic decision.",
    )
    assert result.final_action == "KEEP_DETERMINISTIC_DECISION"


def test_validation_failure_blocks_authorization():
    recommendation = rec()
    from ai.components.decision_validator import ValidationResult
    invalid = ValidationResult(
        incident_id="INC001", recommendation=REVIEW_DUPLICATE, allowed=False,
        confidence=0.9, reasons=(), warnings=(),
        human_authorization_required=True, priority_protected=True,
        responsibility_protected=True, escalation_protected=True,
    )
    with pytest.raises(ValueError):
        HumanAuthorizationGateway().authorize(
            recommendation=recommendation,
            validation=invalid,
            reviewer_id="s",
            reviewer_role="SUPER_ADMIN",
            action=APPROVE,
            reason="x",
        )
