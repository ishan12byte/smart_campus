from dataclasses import dataclass
from datetime import datetime

from decision_engine.categories import validate_category, validate_subcategory

VALID_INCIDENT_STATUSES = {
    "REPORTED",
    "ACKNOWLEDGED",
    "UNDER_REVIEW",
    "ASSIGNED",
    "IN_PROGRESS",
    "VERIFICATION_PENDING",
    "REOPENED",
    # Kept for compatibility with manually managed/back-end records.
    "RESOLVED",
    "CLOSED",
}


def _validate_id(value: int, name: str) -> None:
    if type(value) is not int or value <= 0:
        raise ValueError(f"{name} must be a positive integer.")


def _validate_datetime(value: datetime, name: str) -> None:
    if not isinstance(value, datetime):
        raise TypeError(f"{name} must be a datetime.")


@dataclass
class Report:
    id: int
    description: str
    category: str
    subcategory: str
    location: str
    reported_at: datetime
    reporter_id: int
    session_id: str | None = None
    service_cycle_id: str | None = None

    def __post_init__(self) -> None:
        _validate_id(self.id, "Report id")
        _validate_id(self.reporter_id, "Reporter id")
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("Report description is required.")
        if not isinstance(self.location, str) or not self.location.strip():
            raise ValueError("Report location is required.")
        _validate_datetime(self.reported_at, "Reported time")
        self.category = validate_category(self.category)
        self.subcategory = validate_subcategory(self.category, self.subcategory)


@dataclass
class Incident:
    id: int
    category: str
    subcategory: str
    location: str
    started_at: datetime
    status: str
    report_ids: list[int]
    resolved_at: datetime | None = None
    verified_at: datetime | None = None
    reopened_count: int = 0
    session_id: str | None = None
    service_cycle_id: str | None = None

    def __post_init__(self) -> None:
        _validate_id(self.id, "Incident id")
        if not isinstance(self.location, str) or not self.location.strip():
            raise ValueError("Incident location is required.")
        _validate_datetime(self.started_at, "Incident start time")
        self.category = validate_category(self.category)
        self.subcategory = validate_subcategory(self.category, self.subcategory)
        if self.status not in VALID_INCIDENT_STATUSES:
            raise ValueError(f"Invalid incident status: {self.status}")
        if not isinstance(self.report_ids, list) or any(
            type(report_id) is not int or report_id <= 0 for report_id in self.report_ids
        ):
            raise ValueError("report_ids must contain positive integers.")
        if type(self.reopened_count) is not int or self.reopened_count < 0:
            raise ValueError("reopened_count must be a non-negative integer.")
        if self.resolved_at is not None:
            _validate_datetime(self.resolved_at, "Resolved time")
            if self.resolved_at < self.started_at:
                raise ValueError("Resolved time cannot be before incident start time.")
        if self.verified_at is not None:
            _validate_datetime(self.verified_at, "Verified time")
            if self.resolved_at is None:
                raise ValueError("Verified time requires a resolved time.")
            if self.verified_at < self.resolved_at:
                raise ValueError("Verified time cannot be before resolved time.")
