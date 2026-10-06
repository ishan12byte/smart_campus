from datetime import datetime
from decision_engine.assignment import (
    get_eligible_resources,
    filter_by_capacity,
    select_resource,
    assign_incident,
)
from decision_engine.models import Incident
from decision_engine.workload import Resource


def create_it_incident():
    return Incident(
        id=101,
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        started_at=datetime(2026, 8, 31, 10, 0),
        status="IN_PROGRESS",
        report_ids=[1],
    )


def test_only_resources_from_correct_department_are_eligible():

    incident = create_it_incident()

    resources = [
        Resource(
            id=1,
            name="IT Support",
            department="IT",
            capacity_hours=8,
            assigned_hours=2,
        ),
        Resource(
            id=2,
            name="Maintenance Staff",
            department="MAINTENANCE",
            capacity_hours=8,
            assigned_hours=1,
        ),
    ]

    eligible = get_eligible_resources(
        incident,
        resources,
    )

    assert eligible == [resources[0]]


def test_filter_by_capacity():

    resources = [
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
            assigned_hours=7,
        ),
    ]

    available = filter_by_capacity(
        resources,
        required_hours=3,
    )

    assert available == [resources[0]]


def test_select_resource_with_lowest_workload():

    resources = [
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

    selected = select_resource(resources)

    assert selected is resources[1]


def test_assign_incident():

    incident = create_it_incident()

    resources = [
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

    result = assign_incident(
        incident,
        resources,
        required_hours=3,
    )

    assert result.assigned is True
    assert result.resource is resources[1]
    assert (
        result.reason
        == "Eligible resource with available capacity "
        "and lowest workload."
    )


def test_assignment_fails_when_no_resource_has_capacity():

    incident = create_it_incident()

    resources = [
        Resource(
            id=1,
            name="IT A",
            department="IT",
            capacity_hours=8,
            assigned_hours=7,
        ),
        Resource(
            id=2,
            name="IT B",
            department="IT",
            capacity_hours=8,
            assigned_hours=8,
        ),
    ]

    result = assign_incident(
        incident,
        resources,
        required_hours=2,
    )

    assert result.assigned is False
    assert result.resource is None
    assert (
        result.reason
        == "No eligible resource has sufficient capacity."
    )


def test_assignment_fails_when_no_eligible_department():

    incident = create_it_incident()

    resources = [
        Resource(
            id=1,
            name="Maintenance Staff",
            department="MAINTENANCE",
            capacity_hours=8,
            assigned_hours=2,
        ),
    ]

    result = assign_incident(
        incident,
        resources,
        required_hours=2,
    )

    assert result.assigned is False
    assert result.resource is None
    assert (
        result.reason
        == "No eligible resource is available."
    )