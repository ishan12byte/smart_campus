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

def attach_report_to_incident(
    report: Report,
    incident: Incident,
) -> Incident:

    if report.id not in incident.report_ids:
        incident.report_ids.append(report.id)

    return incident

def create_incident(
    report: Report,
    incident_id: int,
) -> Incident:

    return Incident(
        id=incident_id,
        category=report.category,
        subcategory=report.subcategory,
        location=report.location,
        started_at=report.reported_at,
        status="REPORTED",
        report_ids=[report.id],
    )

def process_report(
    report: Report,
    incidents: list[Incident],
    new_incident_id: int,
) -> tuple[Incident, bool]:

    matching_incident = find_matching_incident(
        report,
        incidents,
    )

    if matching_incident is not None:
        attach_report_to_incident(
            report,
            matching_incident,
        )

        return matching_incident, False

    new_incident = create_incident(
        report,
        new_incident_id,
    )

    incidents.append(new_incident)

    return new_incident, True