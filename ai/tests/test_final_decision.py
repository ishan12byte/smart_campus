from datetime import datetime
from decision_engine.engine import DecisionInput, PriorityInput, ResponsibilityInput, process_decision
from decision_engine.models import Report
from decision_engine.workload import Resource

from ai.components.decision_fusion import DecisionRecommendation, REVIEW_DUPLICATE
from ai.components.decision_validator import DecisionValidator
from ai.components.final_decision import (
    FINAL_AUTHORIZED, FINAL_PENDING_AUTHORIZATION, FINAL_REJECTED,
    build_final_decision,
)
from ai.components.human_authorization import HumanAuthorizationGateway, APPROVE, REJECT


def deterministic():
    return process_decision(
        DecisionInput(
            report=Report(
                id=1, description="Projector broken", category="IT", subcategory="PROJECTOR",
                location="Room 204", reported_at=datetime(2026, 10, 6, 10, 0), reporter_id=1
            ),
            incidents=[], resources=[Resource(1, "IT-1", "IT", 8, 2)], new_incident_id=1,
            priority=PriorityInput(3, 3, 1, 2, 1),
            responsibility=ResponsibilityInput(), required_hours=1,
        )
    )


def recommendation(dec):
    return DecisionRecommendation(
        incident_id=str(dec.incident.id), recommendation=REVIEW_DUPLICATE,
        confidence=.9, reason="review", evidence_signals=("DUPLICATE_REVIEW",),
        supporting_evidence=("related",), limitations=(), human_review_required=True,
        deterministic_priority=dec.priority["level"],
        deterministic_responsibility=dec.responsibility["status"],
        deterministic_department=dec.assignment.resource.department,
        deterministic_escalation=dec.escalation.level,
    )


def test_without_human_auth_is_pending():
    dec = deterministic(); rec = recommendation(dec); val = DecisionValidator().validate(rec)
    final = build_final_decision(dec, rec, val)
    assert final.final_status == FINAL_PENDING_AUTHORIZATION
    assert final.human_authorized is False
    payload = final.to_dict()
    assert payload["incident_id"] == "1"
    assert payload["deterministic_decision"]["priority"]["level"] == "MEDIUM"


def test_approved_is_finally_authorized():
    dec = deterministic(); rec = recommendation(dec); val = DecisionValidator().validate(rec)
    auth = HumanAuthorizationGateway().authorize(
        recommendation=rec, validation=val, reviewer_id="1", reviewer_role="HEAD",
        action=APPROVE, reason="approved",
    )
    final = build_final_decision(dec, rec, val, auth)
    assert final.final_status == FINAL_AUTHORIZED
    assert final.human_authorized is True


def test_rejected_keeps_deterministic_decision():
    dec = deterministic(); rec = recommendation(dec); val = DecisionValidator().validate(rec)
    auth = HumanAuthorizationGateway().authorize(
        recommendation=rec, validation=val, reviewer_id="1", reviewer_role="HEAD",
        action=REJECT, reason="separate incident",
    )
    final = build_final_decision(dec, rec, val, auth)
    assert final.final_status == FINAL_REJECTED
    assert final.final_action == "KEEP_DETERMINISTIC_DECISION"
