from decision_engine.models import Report, Incident
from decision_engine.matching_policy import (
    PERSISTENT,
    SERVICE_CYCLE,
    SESSION,
    get_matching_policy,
)


ACTIVE_STATUSES = {
    "REPORTED",
    "ACKNOWLEDGED",
    "UNDER_REVIEW",
    "ASSIGNED",
    "IN_PROGRESS",
    "REOPENED",
    "VERIFICATION_PENDING",
}


def is_candidate_match(
    report: Report,
    incident: Incident,
) -> bool:
    if incident.status not in ACTIVE_STATUSES:
        return False

    if report.category.strip().upper() != incident.category.strip().upper():
        return False

    if report.subcategory.strip().upper() != incident.subcategory.strip().upper():
        return False

    if report.location.strip().lower() != incident.location.strip().lower():
        return False

    policy = get_matching_policy(report.subcategory)

    if policy == PERSISTENT:
        return True

    if policy == SERVICE_CYCLE:
        return (
            report.service_cycle_id is not None
            and incident.service_cycle_id is not None
            and report.service_cycle_id == incident.service_cycle_id
        )

    if policy == SESSION:
        return (
            report.session_id is not None
            and incident.session_id is not None
            and report.session_id == incident.session_id
        )

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
        session_id=report.session_id,
        service_cycle_id=report.service_cycle_id,
    )


def process_report(
    report: Report,
    incidents: list[Incident],
    new_incident_id: int,
) -> tuple[Incident, bool]:
    matching_incident = find_matching_incident(report, incidents)

    if matching_incident is not None:
        attach_report_to_incident(report, matching_incident)
        return matching_incident, False

    new_incident = create_incident(report, new_incident_id)
    incidents.append(new_incident)
    return new_incident, True
