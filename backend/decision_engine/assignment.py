from dataclasses import dataclass

from decision_engine.models import Incident
from decision_engine.workload import (
    Resource,
    calculate_workload_ratio,
    get_remaining_capacity,
)


@dataclass
class AssignmentResult:
    resource: Resource | None
    assigned: bool
    reason: str


def get_eligible_resources(
    incident: Incident,
    resources: list[Resource],
) -> list[Resource]:

    return [
        resource
        for resource in resources
        if resource.department.strip().upper()
        == incident.category.strip().upper()
    ]


def filter_by_capacity(
    resources: list[Resource],
    required_hours: float,
) -> list[Resource]:

    if required_hours <= 0:
        raise ValueError(
            "Required hours must be greater than zero."
        )

    return [
        resource
        for resource in resources
        if get_remaining_capacity(resource) >= required_hours
    ]


def select_resource(
    resources: list[Resource],
) -> Resource | None:

    if not resources:
        return None

    return min(
        resources,
        key=calculate_workload_ratio,
    )


def assign_incident(
    incident: Incident,
    resources: list[Resource],
    required_hours: float,
) -> AssignmentResult:

    eligible = get_eligible_resources(
        incident,
        resources,
    )

    if not eligible:
        return AssignmentResult(
            resource=None,
            assigned=False,
            reason="No eligible resource is available.",
        )

    available = filter_by_capacity(
        eligible,
        required_hours,
    )

    if not available:
        return AssignmentResult(
            resource=None,
            assigned=False,
            reason="No eligible resource has sufficient capacity.",
        )

    selected = select_resource(available)

    return AssignmentResult(
        resource=selected,
        assigned=True,
        reason=(
            "Eligible resource with available capacity "
            "and lowest workload."
        ),
    )