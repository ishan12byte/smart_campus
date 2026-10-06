from dataclasses import dataclass

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


@dataclass(frozen=True)
class RecurrenceResult:
    incident: Incident
    is_new_incident: bool
    needs_reopen_review: bool = False
    reason: str = ""

    def __iter__(self):
        # Backward-compatible with: incident, is_new = process_report(...)
        yield self.incident
        yield self.is_new_incident


def is_candidate_match(report: Report, incident: Incident) -> bool:
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


def attach_report_to_incident(report: Report, incident: Incident) -> Incident:
    if report.id not in incident.report_ids:
        incident.report_ids.append(report.id)
    return incident


def create_incident(report: Report, incident_id: int) -> Incident:
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
) -> RecurrenceResult:
    matching_incident = find_matching_incident(report, incidents)

    if matching_incident is not None:
        attach_report_to_incident(report, matching_incident)
        needs_reopen_review = matching_incident.status == "VERIFICATION_PENDING"
        reason = (
            "Report attached to an active incident; reopening should be reviewed."
            if needs_reopen_review
            else "Report attached to an existing active incident."
        )
        return RecurrenceResult(
            incident=matching_incident,
            is_new_incident=False,
            needs_reopen_review=needs_reopen_review,
            reason=reason,
        )

    new_incident = create_incident(report, new_incident_id)
    incidents.append(new_incident)
    return RecurrenceResult(
        incident=new_incident,
        is_new_incident=True,
        reason="No active matching incident found; created a new incident.",
    )
