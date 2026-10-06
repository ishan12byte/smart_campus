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


def create_result(level: str, reason: str) -> EscalationResult:
    if level not in VALID_ESCALATION_LEVELS:
        raise ValueError(f"Invalid escalation level: {level}")

    return EscalationResult(
        level=level,
        escalated=level != ESCALATION_NONE,
        reason=reason,
    )


def _ensure_comparable_datetimes(first: datetime, second: datetime) -> None:
    first_aware = first.tzinfo is not None and first.utcoffset() is not None
    second_aware = second.tzinfo is not None and second.utcoffset() is not None
    if first_aware != second_aware:
        raise ValueError("SLA timestamps must both be timezone-aware or both be naive.")


def calculate_sla_violation(
    sla_deadline: datetime | None,
    resolved_at: datetime | None = None,
    reference_time: datetime | None = None,
) -> bool:
    if sla_deadline is None:
        return False

    if not isinstance(sla_deadline, datetime):
        raise TypeError("sla_deadline must be a datetime or None.")

    comparison_time = resolved_at
    if comparison_time is None:
        comparison_time = reference_time
    if comparison_time is None:
        comparison_time = datetime.now(tz=sla_deadline.tzinfo) if sla_deadline.tzinfo else datetime.now()
    if not isinstance(comparison_time, datetime):
        raise TypeError("SLA comparison timestamp must be a datetime.")

    _ensure_comparable_datetimes(sla_deadline, comparison_time)
    return comparison_time > sla_deadline


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

    if priority_level == "CRITICAL":
        return create_result(
            ESCALATION_SUPER_ADMIN,
            "Critical incident requires super admin attention.",
        )
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
