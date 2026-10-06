from dataclasses import dataclass

from decision_engine.models import Incident
from decision_engine.workload import (
    Resource,
    calculate_workload_ratio,
    get_remaining_capacity,
    get_workload_status,
)


@dataclass
class AssignmentResult:
    resource: Resource | None
    assigned: bool
    reason: str
    required_hours: float = 0.0
    workload_ratio: float | None = None
    workload_status: str | None = None
    remaining_capacity: float | None = None


def get_eligible_resources(
    incident: Incident,
    resources: list[Resource],
) -> list[Resource]:
    return [
        resource
        for resource in resources
        if resource.department.strip().upper() == incident.category.strip().upper()
    ]


def filter_by_capacity(
    resources: list[Resource],
    required_hours: float,
) -> list[Resource]:
    if required_hours <= 0:
        raise ValueError("Required hours must be greater than zero.")

    return [
        resource
        for resource in resources
        if get_remaining_capacity(resource) >= required_hours
    ]


def select_resource(resources: list[Resource]) -> Resource | None:
    if not resources:
        return None
    return min(resources, key=calculate_workload_ratio)


def assign_incident(
    incident: Incident,
    resources: list[Resource],
    required_hours: float,
) -> AssignmentResult:
    available_required_hours = required_hours
    eligible = get_eligible_resources(incident, resources)

    if not eligible:
        return AssignmentResult(
            resource=None,
            assigned=False,
            reason="No eligible resource is available.",
            required_hours=available_required_hours,
        )

    available = filter_by_capacity(eligible, required_hours)

    if not available:
        return AssignmentResult(
            resource=None,
            assigned=False,
            reason="No eligible resource has sufficient capacity.",
            required_hours=available_required_hours,
        )

    selected = select_resource(available)
    ratio = calculate_workload_ratio(selected)

    return AssignmentResult(
        resource=selected,
        assigned=True,
        reason=(
            "Eligible resource with available capacity and lowest workload."
        ),
        required_hours=available_required_hours,
        workload_ratio=ratio,
        workload_status=get_workload_status(ratio),
        remaining_capacity=get_remaining_capacity(selected),
    )
