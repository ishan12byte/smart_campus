from datetime import datetime

from decision_engine.models import Incident


def acknowledge_incident(incident: Incident) -> Incident:
    if incident.status != "REPORTED":
        raise ValueError("Only a reported incident can be acknowledged.")

    incident.status = "ACKNOWLEDGED"
    return incident


def start_incident(incident: Incident) -> Incident:
    if incident.status not in {
        "REPORTED",
        "ACKNOWLEDGED",
        "REOPENED",
    }:
        raise ValueError(
            "Incident cannot be moved to IN_PROGRESS from its current status."
        )

    incident.status = "IN_PROGRESS"
    return incident


def mark_resolved(
    incident: Incident,
    resolved_at: datetime | None = None,
) -> Incident:
    if incident.status != "IN_PROGRESS":
        raise ValueError("Only an in-progress incident can be resolved.")

    if resolved_at is None:
        resolved_at = datetime.now()

    if resolved_at < incident.started_at:
        raise ValueError("Resolution time cannot be before incident start time.")

    incident.resolved_at = resolved_at
    incident.status = "VERIFICATION_PENDING"
    return incident


def verify_resolution(
    incident: Incident,
    verified_at: datetime | None = None,
) -> Incident:
    if incident.status != "VERIFICATION_PENDING":
        raise ValueError(
            "Only an incident pending verification can be verified."
        )

    if incident.resolved_at is None:
        raise ValueError("Incident cannot be verified without a resolution time.")

    if verified_at is None:
        verified_at = datetime.now()

    if verified_at < incident.resolved_at:
        raise ValueError(
            "Verification time cannot be before resolution time."
        )

    incident.verified_at = verified_at
    incident.status = "CLOSED"
    return incident


def reopen_incident(incident: Incident) -> Incident:
    if incident.status not in {
        "RESOLVED",
        "VERIFICATION_PENDING",
    }:
        raise ValueError(
            "Only a resolved or verification-pending incident can be reopened."
        )

    incident.reopened_count += 1
    incident.status = "REOPENED"
    return incident
