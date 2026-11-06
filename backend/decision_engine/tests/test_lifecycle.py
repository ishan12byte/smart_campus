from datetime import datetime

import pytest

from decision_engine.models import Incident
from decision_engine.lifecycle import (
    acknowledge_incident,
    start_incident,
    mark_resolved,
    verify_resolution,
    reopen_incident,
)


def create_test_incident():
    return Incident(
        id=101,
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        started_at=datetime(2026, 8, 31, 10, 0),
        status="REPORTED",
        report_ids=[1],
    )


def test_acknowledge_reported_incident():
    incident = create_test_incident()

    acknowledge_incident(incident)

    assert incident.status == "ACKNOWLEDGED"


def test_start_reported_incident():
    incident = create_test_incident()

    start_incident(incident)

    assert incident.status == "IN_PROGRESS"


def test_start_acknowledged_incident():
    incident = create_test_incident()

    acknowledge_incident(incident)
    start_incident(incident)

    assert incident.status == "IN_PROGRESS"


def test_mark_resolved_sets_resolution_time():
    incident = create_test_incident()

    start_incident(incident)

    resolved_at = datetime(2026, 8, 31, 12, 0)

    mark_resolved(
        incident,
        resolved_at,
    )

    assert incident.status == "VERIFICATION_PENDING"
    assert incident.resolved_at == resolved_at


def test_verify_resolution_closes_incident():
    incident = create_test_incident()

    start_incident(incident)

    resolved_at = datetime(2026, 8, 31, 12, 0)
    verified_at = datetime(2026, 8, 31, 12, 30)

    mark_resolved(incident, resolved_at)
    verify_resolution(incident, verified_at)

    assert incident.status == "CLOSED"
    assert incident.resolved_at == resolved_at
    assert incident.verified_at == verified_at


def test_reopen_verification_pending_incident():
    incident = create_test_incident()

    start_incident(incident)

    mark_resolved(
        incident,
        datetime(2026, 8, 31, 12, 0),
    )

    reopen_incident(incident)

    assert incident.status == "REOPENED"


def test_reopened_incident_can_start_again():
    incident = create_test_incident()

    start_incident(incident)

    mark_resolved(
        incident,
        datetime(2026, 8, 31, 12, 0),
    )

    reopen_incident(incident)
    start_incident(incident)

    assert incident.status == "IN_PROGRESS"

def test_cannot_resolve_reported_incident():
    incident = create_test_incident()

    with pytest.raises(ValueError):
        mark_resolved(
            incident,
            datetime(2026, 8, 31, 12, 0),
        )


def test_cannot_verify_without_resolution():
    incident = create_test_incident()

    with pytest.raises(ValueError):
        verify_resolution(
            incident,
            datetime(2026, 8, 31, 12, 30),
        )


def test_resolution_cannot_be_before_start():
    incident = create_test_incident()

    start_incident(incident)

    with pytest.raises(ValueError):
        mark_resolved(
            incident,
            datetime(2026, 8, 31, 9, 0),
        )


def test_verification_cannot_be_before_resolution():
    incident = create_test_incident()

    start_incident(incident)

    mark_resolved(
        incident,
        datetime(2026, 8, 31, 12, 0),
    )

    with pytest.raises(ValueError):
        verify_resolution(
            incident,
            datetime(2026, 8, 31, 11, 30),
        )

def test_first_reopen_increments_reopened_count():
    incident = create_test_incident()
    start_incident(incident)
    mark_resolved(incident, datetime(2026, 8, 31, 12, 0))

    assert incident.reopened_count == 0

    reopen_incident(incident)

    assert incident.reopened_count == 1


def test_second_reopen_increments_reopened_count_again():
    incident = create_test_incident()
    start_incident(incident)
    mark_resolved(incident, datetime(2026, 8, 31, 12, 0))
    reopen_incident(incident)

    # Simulate the next resolution cycle.
    start_incident(incident)
    mark_resolved(incident, datetime(2026, 8, 31, 14, 0))
    reopen_incident(incident)

    assert incident.reopened_count == 2
