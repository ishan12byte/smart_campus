from dataclasses import dataclass

@dataclass
class Resource:
    id: int
    name: str
    department: str
    capacity_hours: float
    assigned_hours: float = 0.0


def calculate_workload_ratio(
    resource: Resource,
) -> float:

    if resource.capacity_hours <= 0:
        raise ValueError(
            "Capacity hours must be greater than zero."
        )

    return resource.assigned_hours / resource.capacity_hours


def get_workload_status(
    workload_ratio: float,
) -> str:

    if workload_ratio < 0:
        raise ValueError(
            "Workload ratio cannot be negative."
        )

    if workload_ratio <= 0.70:
        return "NORMAL"

    if workload_ratio <= 0.90:
        return "HIGH"

    if workload_ratio <= 1.00:
        return "VERY_HIGH"

    return "OVERLOADED"


def get_remaining_capacity(
    resource: Resource,
) -> float:

    remaining = (
        resource.capacity_hours
        - resource.assigned_hours
    )

    return max(remaining, 0.0)