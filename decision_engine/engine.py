from dataclasses import asdict, dataclass, field
from datetime import datetime

from decision_engine.assignment import AssignmentResult, assign_incident
from decision_engine.escalation import (
    EscalationResult,
    calculate_sla_violation,
    determine_escalation,
)
from decision_engine.models import Incident, Report
from decision_engine.priority import calculate_priority
from decision_engine.recurrence import RecurrenceResult, process_report
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
    responsibility: ResponsibilityInput = field(default_factory=ResponsibilityInput)
    required_hours: float = 1.0
    sla_deadline: datetime | None = None
    reference_time: datetime | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.report, Report):
            raise TypeError("report must be a Report.")
        if not isinstance(self.incidents, list):
            raise TypeError("incidents must be a list.")
        if not isinstance(self.resources, list):
            raise TypeError("resources must be a list.")
        if any(not isinstance(incident, Incident) for incident in self.incidents):
            raise TypeError("incidents must contain Incident objects.")
        if any(not isinstance(resource, Resource) for resource in self.resources):
            raise TypeError("resources must contain Resource objects.")
        if type(self.new_incident_id) is not int or self.new_incident_id <= 0:
            raise ValueError("new_incident_id must be a positive integer.")
        if self.required_hours <= 0:
            raise ValueError("required_hours must be greater than zero.")
        if self.sla_deadline is not None and not isinstance(self.sla_deadline, datetime):
            raise TypeError("sla_deadline must be a datetime or None.")
        if self.reference_time is not None and not isinstance(self.reference_time, datetime):
            raise TypeError("reference_time must be a datetime or None.")


@dataclass
class DecisionResult:
    incident: Incident
    is_new_incident: bool
    priority: dict
    responsibility: dict
    assignment: AssignmentResult
    escalation: EscalationResult
    recurrence: RecurrenceResult | None = None
    sla_violated: bool = False
    explanation: str = ""

    def to_dict(self) -> dict:
        """Return a JSON-friendly contract for the backend layer."""
        return asdict(self)


def _build_explanation(
    recurrence: RecurrenceResult,
    assignment: AssignmentResult,
    escalation: EscalationResult,
) -> str:
    parts = [recurrence.reason]
    if assignment.assigned:
        parts.append("A capable resource with sufficient capacity was selected.")
    else:
        parts.append(assignment.reason)
    parts.append(escalation.reason)
    return " ".join(parts)


def process_decision(decision_input: DecisionInput) -> DecisionResult:
    """Run the complete deterministic decision pipeline."""
    recurrence = process_report(
        decision_input.report,
        decision_input.incidents,
        decision_input.new_incident_id,
    )
    incident = recurrence.incident

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
        department_expected_to_handle=responsibility_input.department_expected_to_handle,
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
        is_new_incident=recurrence.is_new_incident,
        priority=priority,
        responsibility=responsibility,
        assignment=assignment,
        escalation=escalation,
        recurrence=recurrence,
        sla_violated=sla_violated,
        explanation=_build_explanation(recurrence, assignment, escalation),
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

    if sla_violated and not result.sla_violated:
        result.sla_violated = True
        if not result.escalation.escalated:
            result.escalation = determine_escalation(
                priority_level=result.priority["level"],
                assignment_successful=result.assignment.assigned,
                resource_constraint=resource_constraint,
                reopened_count=result.incident.reopened_count,
                sla_violated=True,
            )
            result.explanation = _build_explanation(
                result.recurrence,
                result.assignment,
                result.escalation,
            )

    return result
