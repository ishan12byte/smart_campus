from dataclasses import dataclass
from datetime import datetime


ESCALATION_NONE = "NONE"
ESCALATION_DEPARTMENT_HEAD = "DEPARTMENT_HEAD"
ESCALATION_SUPER_ADMIN = "SUPER_ADMIN"


VALID_ESCALATION_LEVELS = {
    ESCALATION_NONE,
    ESCALATION_DEPARTMENT_HEAD,
    ESCALATION_SUPER_ADMIN,
}


@dataclass
class EscalationResult:
    level: str
    escalated: bool
    reason: str


def create_result(
    level: str,
    reason: str,
) -> EscalationResult:
    if level not in VALID_ESCALATION_LEVELS:
        raise ValueError(f"Invalid escalation level: {level}")

    return EscalationResult(
        level=level,
        escalated=level != ESCALATION_NONE,
        reason=reason,
    )


def calculate_sla_violation(
    sla_deadline: datetime | None,
    resolved_at: datetime | None = None,
    reference_time: datetime | None = None,
) -> bool:
    """Return whether an incident missed its SLA deadline.

    For an already-resolved incident, the resolution timestamp is compared
    with the deadline. For an active incident, the supplied reference time
    (or the current time) is compared with the deadline.
    """
    if sla_deadline is None:
        return False

    if resolved_at is not None:
        return resolved_at > sla_deadline

    if reference_time is None:
        reference_time = datetime.now()

    return reference_time > sla_deadline


def determine_escalation(
    priority_level: str,
    assignment_successful: bool,
    resource_constraint: bool = False,
    reopened_count: int = 0,
    sla_violated: bool = False,
) -> EscalationResult:
    if not priority_level or not isinstance(priority_level, str):
        raise ValueError("Priority level is required.")

    priority_level = priority_level.strip().upper()

    if priority_level not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
        raise ValueError(f"Invalid priority level: {priority_level}")

    if not isinstance(assignment_successful, bool):
        raise TypeError("assignment_successful must be a boolean.")

    if not isinstance(resource_constraint, bool):
        raise TypeError("resource_constraint must be a boolean.")

    if not isinstance(sla_violated, bool):
        raise TypeError("sla_violated must be a boolean.")

    if type(reopened_count) is not int:
        raise TypeError("reopened_count must be an integer.")

    if reopened_count < 0:
        raise ValueError("Reopened count cannot be negative.")

    # Critical incidents always require institution-level attention.
    if priority_level == "CRITICAL":
        return create_result(
            ESCALATION_SUPER_ADMIN,
            "Critical incident requires super admin attention.",
        )

    # Resource constraints, failed assignment, repeated reopening,
    # or SLA violation require department-level intervention.
    if resource_constraint:
        return create_result(
            ESCALATION_DEPARTMENT_HEAD,
            "Resource constraint requires department-level intervention.",
        )

    if not assignment_successful:
        return create_result(
            ESCALATION_DEPARTMENT_HEAD,
            "Incident could not be assigned to an eligible resource.",
        )

    if reopened_count >= 2:
        return create_result(
            ESCALATION_DEPARTMENT_HEAD,
            "Incident has been repeatedly reopened.",
        )

    if sla_violated:
        return create_result(
            ESCALATION_DEPARTMENT_HEAD,
            "Incident has violated its expected service timeline.",
        )

    return create_result(
        ESCALATION_NONE,
        "No escalation condition has been triggered.",
    )
