from dataclasses import dataclass


@dataclass
class Resource:
    id: int
    name: str
    department: str
    capacity_hours: float
    assigned_hours: float = 0.0

    def __post_init__(self) -> None:
        if type(self.id) is not int or self.id <= 0:
            raise ValueError("Resource id must be a positive integer.")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Resource name is required.")
        if not isinstance(self.department, str) or not self.department.strip():
            raise ValueError("Resource department is required.")
        if self.assigned_hours < 0:
            raise ValueError("Assigned hours cannot be negative.")


def calculate_workload_ratio(resource: Resource) -> float:
    if resource.capacity_hours <= 0:
        raise ValueError("Capacity hours must be greater than zero.")
    return resource.assigned_hours / resource.capacity_hours


def get_workload_status(workload_ratio: float) -> str:
    if workload_ratio < 0:
        raise ValueError("Workload ratio cannot be negative.")

    if workload_ratio <= 0.70:
        return "NORMAL"
    if workload_ratio <= 0.90:
        return "HIGH"
    if workload_ratio <= 1.00:
        return "VERY_HIGH"
    return "OVERLOADED"


def get_remaining_capacity(resource: Resource) -> float:
    return max(resource.capacity_hours - resource.assigned_hours, 0.0)
