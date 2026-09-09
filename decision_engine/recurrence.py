from datetime import datetime

from decision_engine.models import Report, Incident
from decision_engine.matching_policy import (
    PERSISTENT,
    SERVICE_CYCLE,
    SESSION,
    get_matching_policy,
)


ACTIVE_STATUSES = {
    "REPORTED",
    "UNDER_REVIEW",
    "ASSIGNED",
    "IN_PROGRESS",
}


def time_difference_minutes(
    time_a: datetime,
    time_b: datetime,
) -> float:
    difference = abs((time_a - time_b).total_seconds())
    return difference / 60


def is_candidate_match(
    report: Report,
    incident: Incident,
) -> bool:

    # A completed incident should not normally
    # receive new reports as part of the same occurrence.
    if incident.status not in ACTIVE_STATUSES:
        return False

    # Category must match.
    if report.category.upper() != incident.category.upper():
        return False

    # Subcategory must match.
    if report.subcategory.upper() != incident.subcategory.upper():
        return False

    # Location must match.
    if report.location.strip().lower() != incident.location.strip().lower():
        return False

    policy = get_matching_policy(report.subcategory)

    # Persistent problems can remain active for hours or days.
    # Therefore, we do not use a fixed time window.
    if policy == PERSISTENT:
        return True

    # These policies will get additional context-based
    # matching logic in the next step.
    if policy == SERVICE_CYCLE:
        return True

    if policy == SESSION:
        return True

    return False

def find_matching_incident(
    report: Report,
    incidents: list[Incident],
) -> Incident | None:

    for incident in incidents:
        if is_candidate_match(report, incident):
            return incident

    return None