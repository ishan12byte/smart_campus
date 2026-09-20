from dataclasses import dataclass
from datetime import datetime


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
