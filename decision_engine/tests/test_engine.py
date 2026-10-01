from datetime import datetime
from decision_engine.engine import process_incident
from decision_engine.models import Report
from decision_engine.workload import Resource


def create_report():
    return Report(
        id=1,
        description="Projector is not working in Room 203.",
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        reported_at=datetime(2026, 9, 14, 10, 0),
        reporter_id=101,
    )


def create_resources():
    return [
        Resource(
            id=1,
            name="IT A",
            department="IT",
            capacity_hours=8,
            assigned_hours=4,
        ),
        Resource(
            id=2,
            name="IT B",
            department="IT",
            capacity_hours=8,
            assigned_hours=2,
        ),
    ]


def test_process_normal_incident():

    report = create_report()
    resources = create_resources()
    incidents = []

    result = process_incident(
        report=report,
        incidents=incidents,
        resources=resources,
        new_incident_id=100,
        impact=3,
        urgency=3,
        safety=1,
        deadline=2,
        recurrence=1,
        required_hours=2,
    )

    assert result.is_new_incident is True

    assert result.incident.id == 100
    assert result.incident.report_ids == [1]

    assert result.priority["level"] == "MEDIUM"

    assert result.assignment.assigned is True
    assert result.assignment.resource is resources[1]

    assert result.escalation.escalated is False

def test_critical_incident_escalates_to_super_admin():

    report = create_report()
    resources = create_resources()
    incidents = []

    result = process_incident(
        report=report,
        incidents=incidents,
        resources=resources,
        new_incident_id=200,
        impact=5,
        urgency=5,
        safety=5,
        deadline=5,
        recurrence=5,
        incident_type="FIRE",
        required_hours=2,
    )

    assert result.priority["level"] == "CRITICAL"

    assert result.escalation.escalated is True
    assert result.escalation.level == "SUPER_ADMIN"

def test_assignment_failure_escalates_to_department_head():

    report = create_report()

    resources = [
        Resource(
            id=1,
            name="IT A",
            department="IT",
            capacity_hours=8,
            assigned_hours=8,
        )
    ]

    incidents = []

    result = process_incident(
        report=report,
        incidents=incidents,
        resources=resources,
        new_incident_id=201,
        impact=3,
        urgency=3,
        safety=2,
        deadline=2,
        recurrence=1,
        required_hours=2,
    )

    assert result.assignment.assigned is False

    assert result.escalation.level == "DEPARTMENT_HEAD"
    assert result.escalation.escalated is True

def test_user_caused_incident_gets_user_caused_recommendation():

    report = create_report()
    resources = create_resources()
    incidents = []

    result = process_incident(
        report=report,
        incidents=incidents,
        resources=resources,
        new_incident_id=202,
        impact=2,
        urgency=2,
        safety=1,
        deadline=1,
        recurrence=1,
        user_caused=True,
        required_hours=1,
    )

    assert result.responsibility["status"] == "USER_CAUSED"
    assert result.responsibility["confidence"] == 0.90

def test_infrastructure_failure_recommendation():

    report = create_report()
    resources = create_resources()
    incidents = []

    result = process_incident(
        report=report,
        incidents=incidents,
        resources=resources,
        new_incident_id=203,
        impact=4,
        urgency=4,
        safety=3,
        deadline=3,
        recurrence=2,
        infrastructure_failed=True,
        required_hours=1,
    )

    assert (
        result.responsibility["status"]
        == "INFRASTRUCTURE_FAILURE"
    )

def test_multiple_reports_attach_to_same_incident():

    first_report = Report(
        id=10,
        description="Projector is broken.",
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        reported_at=datetime(2026, 9, 14, 10, 0),
        reporter_id=101,
    )

    second_report = Report(
        id=11,
        description="The projector in Room 203 still does not work.",
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        reported_at=datetime(2026, 9, 14, 11, 0),
        reporter_id=102,
    )

    resources = create_resources()
    incidents = []

    first_result = process_incident(
        report=first_report,
        incidents=incidents,
        resources=resources,
        new_incident_id=300,
        impact=3,
        urgency=3,
        safety=1,
        deadline=2,
        recurrence=1,
        required_hours=1,
    )

    second_result = process_incident(
        report=second_report,
        incidents=incidents,
        resources=resources,
        new_incident_id=301,
        impact=3,
        urgency=3,
        safety=1,
        deadline=2,
        recurrence=1,
        required_hours=1,
    )

    assert first_result.incident.id == 300

    assert second_result.is_new_incident is False

    assert second_result.incident.id == 300

    assert second_result.incident.report_ids == [10, 11]

    assert len(incidents) == 1


def test_new_report_after_closed_incident_creates_new_incident():

    first_report = Report(
        id=20,
        description="Projector is broken.",
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        reported_at=datetime(2026, 9, 14, 10, 0),
        reporter_id=101,
    )

    second_report = Report(
        id=21,
        description="Projector has broken again.",
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        reported_at=datetime(2026, 9, 17, 10, 0),
        reporter_id=102,
    )

    resources = create_resources()
    incidents = []

    first_result = process_incident(
        report=first_report,
        incidents=incidents,
        resources=resources,
        new_incident_id=400,
        impact=3,
        urgency=3,
        safety=1,
        deadline=2,
        recurrence=1,
        required_hours=1,
    )

    first_incident = first_result.incident

    # Simulate successful resolution.
    first_incident.status = "CLOSED"

    second_result = process_incident(
        report=second_report,
        incidents=incidents,
        resources=resources,
        new_incident_id=401,
        impact=3,
        urgency=3,
        safety=1,
        deadline=2,
        recurrence=2,
        required_hours=1,
    )

    assert second_result.is_new_incident is True

    assert second_result.incident.id == 401

    assert second_result.incident.id != first_incident.id

    assert len(incidents) == 2

def test_resource_constraint_escalates_even_when_assignment_succeeds():
    report = create_report()
    resources = create_resources()
    incidents = []

    result = process_incident(
        report=report,
        incidents=incidents,
        resources=resources,
        new_incident_id=500,
        impact=3,
        urgency=3,
        safety=2,
        deadline=2,
        recurrence=1,
        resource_constraint=True,
        required_hours=1,
    )

    assert result.assignment.assigned is True
    assert result.escalation.level == "DEPARTMENT_HEAD"


def test_engine_passes_reopened_count_to_escalation():
    report = create_report()
    resources = create_resources()

    incident = process_incident(
        report=report,
        incidents=[],
        resources=resources,
        new_incident_id=501,
        impact=3,
        urgency=3,
        safety=2,
        deadline=2,
        recurrence=1,
        required_hours=1,
    ).incident

    incident.status = "REOPENED"
    incident.reopened_count = 2

    result = process_incident(
        report=Report(
            id=2,
            description="Projector still broken",
            category="IT",
            subcategory="PROJECTOR",
            location="Room 203",
            reported_at=datetime(2026, 9, 14, 12, 0),
            reporter_id=102,
        ),
        incidents=[incident],
        resources=resources,
        new_incident_id=502,
        impact=3,
        urgency=3,
        safety=2,
        deadline=2,
        recurrence=2,
        required_hours=1,
    )

    assert result.incident is incident
    assert result.escalation.level == "DEPARTMENT_HEAD"

from decision_engine.engine import (
    DecisionInput,
    PriorityInput,
    ResponsibilityInput,
    process_decision,
)


def test_structured_decision_input_runs_complete_pipeline():
    result = process_decision(
        DecisionInput(
            report=create_report(),
            incidents=[],
            resources=create_resources(),
            new_incident_id=600,
            priority=PriorityInput(
                impact=3,
                urgency=3,
                safety=1,
                deadline=2,
                recurrence=1,
            ),
            responsibility=ResponsibilityInput(),
            required_hours=1,
        )
    )

    assert result.is_new_incident is True
    assert result.assignment.assigned is True
    assert result.escalation.escalated is False


def test_structured_input_calculates_sla_violation():
    report = create_report()
    result = process_decision(
        DecisionInput(
            report=report,
            incidents=[],
            resources=create_resources(),
            new_incident_id=601,
            priority=PriorityInput(
                impact=3,
                urgency=3,
                safety=1,
                deadline=2,
                recurrence=1,
            ),
            responsibility=ResponsibilityInput(),
            required_hours=1,
            sla_deadline=datetime(2026, 9, 14, 9, 0),
            reference_time=datetime(2026, 9, 14, 10, 0),
        )
    )

    assert result.escalation.level == "DEPARTMENT_HEAD"
    assert result.escalation.escalated is True
