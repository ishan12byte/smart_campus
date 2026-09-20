from dataclasses import dataclass
from datetime import datetime

from decision_engine.assignment import AssignmentResult, assign_incident
from decision_engine.escalation import (
    EscalationResult,
    calculate_sla_violation,
    determine_escalation,
)
from decision_engine.models import Incident, Report
from decision_engine.priority import calculate_priority
from decision_engine.recurrence import process_report
from decision_engine.responsibility import determine_responsibility
from decision_engine.workload import Resource


@dataclass(frozen=True)
class PriorityInput:
    impact: int
    urgency: int
    safety: int
    deadline: int
    recurrence: int
    incident_type: str | None = None


@dataclass(frozen=True)
class ResponsibilityInput:
    evidence_available: bool = False
    department_expected_to_handle: bool = True
    service_was_provided: bool | None = None
    user_caused: bool = False
    infrastructure_failed: bool = False
    external_cause: bool = False
    resource_constraint: bool = False
    process_failed: bool = False


@dataclass(frozen=True)
class DecisionInput:
    report: Report
    incidents: list[Incident]
    resources: list[Resource]
    new_incident_id: int
    priority: PriorityInput
    responsibility: ResponsibilityInput = ResponsibilityInput()
    required_hours: float = 1.0
    sla_deadline: datetime | None = None
    reference_time: datetime | None = None


@dataclass
class DecisionResult:
    incident: Incident
    is_new_incident: bool
    priority: dict
    responsibility: dict
    assignment: AssignmentResult
    escalation: EscalationResult


def process_decision(decision_input: DecisionInput) -> DecisionResult:
    """Run the complete deterministic decision pipeline."""
    incident, is_new_incident = process_report(
        decision_input.report,
        decision_input.incidents,
        decision_input.new_incident_id,
    )

    priority_input = decision_input.priority
    priority = calculate_priority(
        impact=priority_input.impact,
        urgency=priority_input.urgency,
        safety=priority_input.safety,
        deadline=priority_input.deadline,
        recurrence=priority_input.recurrence,
        incident_type=priority_input.incident_type,
    )

    responsibility_input = decision_input.responsibility
    responsibility = determine_responsibility(
        category=decision_input.report.category,
        evidence_available=responsibility_input.evidence_available,
        department_expected_to_handle=(
            responsibility_input.department_expected_to_handle
        ),
        service_was_provided=responsibility_input.service_was_provided,
        user_caused=responsibility_input.user_caused,
        infrastructure_failed=responsibility_input.infrastructure_failed,
        external_cause=responsibility_input.external_cause,
        resource_constraint=responsibility_input.resource_constraint,
        process_failed=responsibility_input.process_failed,
    )

    assignment = assign_incident(
        incident=incident,
        resources=decision_input.resources,
        required_hours=decision_input.required_hours,
    )

    sla_violated = calculate_sla_violation(
        sla_deadline=decision_input.sla_deadline,
        resolved_at=incident.resolved_at,
        reference_time=decision_input.reference_time,
    )

    escalation = determine_escalation(
        priority_level=priority["level"],
        assignment_successful=assignment.assigned,
        resource_constraint=responsibility_input.resource_constraint,
        reopened_count=incident.reopened_count,
        sla_violated=sla_violated,
    )

    return DecisionResult(
        incident=incident,
        is_new_incident=is_new_incident,
        priority=priority,
        responsibility=responsibility,
        assignment=assignment,
        escalation=escalation,
    )


def process_incident(
    report: Report,
    incidents: list[Incident],
    resources: list[Resource],
    new_incident_id: int,
    impact: int,
    urgency: int,
    safety: int,
    deadline: int,
    recurrence: int,
    incident_type: str | None = None,
    evidence_available: bool = False,
    department_expected_to_handle: bool = True,
    service_was_provided: bool | None = None,
    user_caused: bool = False,
    infrastructure_failed: bool = False,
    external_cause: bool = False,
    resource_constraint: bool = False,
    process_failed: bool = False,
    required_hours: float = 1.0,
    sla_violated: bool = False,
) -> DecisionResult:
    """Backward-compatible wrapper around the structured decision API."""
    decision_input = DecisionInput(
        report=report,
        incidents=incidents,
        resources=resources,
        new_incident_id=new_incident_id,
        priority=PriorityInput(
            impact=impact,
            urgency=urgency,
            safety=safety,
            deadline=deadline,
            recurrence=recurrence,
            incident_type=incident_type,
        ),
        responsibility=ResponsibilityInput(
            evidence_available=evidence_available,
            department_expected_to_handle=department_expected_to_handle,
            service_was_provided=service_was_provided,
            user_caused=user_caused,
            infrastructure_failed=infrastructure_failed,
            external_cause=external_cause,
            resource_constraint=resource_constraint,
            process_failed=process_failed,
        ),
        required_hours=required_hours,
    )

    result = process_decision(decision_input)

    # This legacy wrapper receives an already-computed SLA result. Keep it
    # authoritative for compatibility while the structured API uses timestamps.
    if sla_violated and not result.escalation.escalated:
        result.escalation = determine_escalation(
            priority_level=result.priority["level"],
            assignment_successful=result.assignment.assigned,
            resource_constraint=resource_constraint,
            reopened_count=result.incident.reopened_count,
            sla_violated=True,
        )

    return result
