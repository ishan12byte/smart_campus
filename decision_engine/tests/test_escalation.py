from decision_engine.escalation import (
    ESCALATION_NONE,
    ESCALATION_DEPARTMENT_HEAD,
    ESCALATION_SUPER_ADMIN,
    determine_escalation,
)


def test_no_escalation_for_normal_successful_assignment():

    result = determine_escalation(
        priority_level="MEDIUM",
        assignment_successful=True,
    )

    assert result.level == ESCALATION_NONE
    assert result.escalated is False


def test_escalates_when_assignment_fails():

    result = determine_escalation(
        priority_level="HIGH",
        assignment_successful=False,
    )

    assert result.level == ESCALATION_DEPARTMENT_HEAD
    assert result.escalated is True


def test_escalates_when_resource_constraint_exists():

    result = determine_escalation(
        priority_level="HIGH",
        assignment_successful=True,
        resource_constraint=True,
    )

    assert result.level == ESCALATION_DEPARTMENT_HEAD
    assert result.escalated is True


def test_critical_incident_escalates_to_super_admin():

    result = determine_escalation(
        priority_level="CRITICAL",
        assignment_successful=True,
    )

    assert result.level == ESCALATION_SUPER_ADMIN
    assert result.escalated is True


def test_critical_incident_with_resource_constraint_still_goes_to_super_admin():

    result = determine_escalation(
        priority_level="CRITICAL",
        assignment_successful=False,
        resource_constraint=True,
    )

    assert result.level == ESCALATION_SUPER_ADMIN
    assert result.escalated is True


def test_repeated_reopening_triggers_escalation():

    result = determine_escalation(
        priority_level="HIGH",
        assignment_successful=True,
        reopened_count=2,
    )

    assert result.level == ESCALATION_DEPARTMENT_HEAD
    assert result.escalated is True


def test_sla_violation_triggers_escalation():

    result = determine_escalation(
        priority_level="HIGH",
        assignment_successful=True,
        sla_violated=True,
    )

    assert result.level == ESCALATION_DEPARTMENT_HEAD
    assert result.escalated is True


def test_one_reopening_does_not_automatically_escalate():

    result = determine_escalation(
        priority_level="MEDIUM",
        assignment_successful=True,
        reopened_count=1,
    )

    assert result.level == ESCALATION_NONE
    assert result.escalated is False
from datetime import datetime

from decision_engine.escalation import calculate_sla_violation


def test_sla_is_not_violated_when_no_deadline_exists():
    assert calculate_sla_violation(None) is False


def test_active_incident_violates_sla_after_deadline():
    assert calculate_sla_violation(
        sla_deadline=datetime(2026, 9, 14, 12, 0),
        reference_time=datetime(2026, 9, 14, 12, 1),
    ) is True


def test_active_incident_does_not_violate_sla_before_deadline():
    assert calculate_sla_violation(
        sla_deadline=datetime(2026, 9, 14, 12, 0),
        reference_time=datetime(2026, 9, 14, 11, 59),
    ) is False


def test_resolved_incident_uses_resolution_time_for_sla():
    assert calculate_sla_violation(
        sla_deadline=datetime(2026, 9, 14, 12, 0),
        resolved_at=datetime(2026, 9, 14, 12, 30),
        reference_time=datetime(2026, 9, 14, 11, 0),
    ) is True
