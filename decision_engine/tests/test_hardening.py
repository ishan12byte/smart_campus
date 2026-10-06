from datetime import datetime, timezone

import pytest

from decision_engine.assignment import assign_incident
from decision_engine.categories import validate_category, validate_subcategory
from decision_engine.engine import DecisionInput, PriorityInput, process_decision
from decision_engine.escalation import calculate_sla_violation
from decision_engine.lifecycle import reopen_incident
from decision_engine.models import Incident, Report
from decision_engine.recurrence import process_report
from decision_engine.workload import Resource


def make_report(**overrides):
    data = dict(
        id=1,
        description="Projector is not working in Room 203.",
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        reported_at=datetime(2026, 9, 15, 9, 0),
        reporter_id=101,
    )
    data.update(overrides)
    return Report(**data)


def make_incident(**overrides):
    data = dict(
        id=100,
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        started_at=datetime(2026, 9, 15, 8, 0),
        status="VERIFICATION_PENDING",
        report_ids=[10],
        resolved_at=datetime(2026, 9, 15, 8, 30),
    )
    data.update(overrides)
    return Incident(**data)


def test_report_matching_verification_pending_requests_reopen_review_without_auto_reopen():
    incident = make_incident()
    report = make_report(id=2)

    result = process_report(report, [incident], new_incident_id=200)

    assert result.is_new_incident is False
    assert result.incident is incident
    assert result.needs_reopen_review is True
    assert incident.status == "VERIFICATION_PENDING"
    assert incident.reopened_count == 0
    assert incident.report_ids == [10, 2]


def test_reopen_is_an_explicit_lifecycle_action():
    incident = make_incident()

    reopen_incident(incident)

    assert incident.status == "REOPENED"
    assert incident.reopened_count == 1
    assert incident.verified_at is None


def test_models_reject_invalid_domain_values():
    with pytest.raises(ValueError):
        validate_category("UNKNOWN")

    with pytest.raises(ValueError):
        validate_subcategory("IT", "WASHROOM")

    with pytest.raises(ValueError):
        make_report(category="UNKNOWN")

    with pytest.raises(ValueError):
        Resource(id=1, name="IT", department="IT", capacity_hours=8, assigned_hours=-1)


def test_zero_capacity_is_still_rejected_when_used_for_workload_calculation():
    resource = Resource(id=1, name="IT", department="IT", capacity_hours=0)
    with pytest.raises(ValueError):
        from decision_engine.workload import calculate_workload_ratio
        calculate_workload_ratio(resource)


def test_assignment_result_exposes_workload_metadata():
    incident = Incident(
        id=101,
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        started_at=datetime(2026, 9, 15, 8, 0),
        status="IN_PROGRESS",
        report_ids=[1],
    )
    resources = [
        Resource(id=1, name="A", department="IT", capacity_hours=8, assigned_hours=2),
        Resource(id=2, name="B", department="IT", capacity_hours=8, assigned_hours=4),
    ]

    result = assign_incident(incident, resources, required_hours=2)

    assert result.assigned is True
    assert result.required_hours == 2
    assert result.workload_ratio == 0.25
    assert result.workload_status == "NORMAL"
    assert result.remaining_capacity == 6


def test_sla_uses_deadline_timezone_and_rejects_mixed_awareness():
    deadline = datetime(2026, 9, 15, 10, 0, tzinfo=timezone.utc)
    reference = datetime(2026, 9, 15, 10, 1, tzinfo=timezone.utc)
    assert calculate_sla_violation(deadline, reference_time=reference) is True

    with pytest.raises(ValueError):
        calculate_sla_violation(
            deadline,
            reference_time=datetime(2026, 9, 15, 10, 1),
        )


def test_structured_result_has_stable_contract_and_explanation():
    report = make_report()
    resources = [
        Resource(id=1, name="IT A", department="IT", capacity_hours=8, assigned_hours=2)
    ]
    result = process_decision(
        DecisionInput(
            report=report,
            incidents=[],
            resources=resources,
            new_incident_id=500,
            priority=PriorityInput(impact=3, urgency=3, safety=1, deadline=2, recurrence=1),
            required_hours=1,
        )
    )

    payload = result.to_dict()
    assert set(payload) == {
        "incident",
        "is_new_incident",
        "priority",
        "responsibility",
        "assignment",
        "escalation",
        "recurrence",
        "sla_violated",
        "explanation",
    }
    assert payload["recurrence"]["is_new_incident"] is True
    assert result.explanation
