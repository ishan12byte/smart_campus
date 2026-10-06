from datetime import datetime

from decision_engine.models import Incident, VALID_INCIDENT_STATUSES


STATUS_REPORTED = "REPORTED"
STATUS_ACKNOWLEDGED = "ACKNOWLEDGED"
STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_VERIFICATION_PENDING = "VERIFICATION_PENDING"
STATUS_REOPENED = "REOPENED"
STATUS_CLOSED = "CLOSED"


def _validate_datetime(value: datetime, name: str) -> None:
    if not isinstance(value, datetime):
        raise TypeError(f"{name} must be a datetime.")


def acknowledge_incident(incident: Incident) -> Incident:
    if incident.status != STATUS_REPORTED:
        raise ValueError("Only a reported incident can be acknowledged.")
    incident.status = STATUS_ACKNOWLEDGED
    return incident


def start_incident(incident: Incident) -> Incident:
    if incident.status not in {
        STATUS_REPORTED,
        STATUS_ACKNOWLEDGED,
        STATUS_REOPENED,
    }:
        raise ValueError(
            "Incident cannot be moved to IN_PROGRESS from its current status."
        )
    incident.status = STATUS_IN_PROGRESS
    return incident


def mark_resolved(
    incident: Incident,
    resolved_at: datetime | None = None,
) -> Incident:
    if incident.status != STATUS_IN_PROGRESS:
        raise ValueError("Only an in-progress incident can be resolved.")

    if resolved_at is None:
        resolved_at = datetime.now()
    _validate_datetime(resolved_at, "Resolved time")

    if resolved_at < incident.started_at:
        raise ValueError("Resolution time cannot be before incident start time.")

    incident.resolved_at = resolved_at
    incident.verified_at = None
    incident.status = STATUS_VERIFICATION_PENDING
    return incident


def verify_resolution(
    incident: Incident,
    verified_at: datetime | None = None,
) -> Incident:
    if incident.status != STATUS_VERIFICATION_PENDING:
        raise ValueError(
            "Only an incident pending verification can be verified."
        )

    if incident.resolved_at is None:
        raise ValueError("Incident cannot be verified without a resolution time.")

    if verified_at is None:
        verified_at = datetime.now()
    _validate_datetime(verified_at, "Verified time")

    if verified_at < incident.resolved_at:
        raise ValueError("Verification time cannot be before resolution time.")

    incident.verified_at = verified_at
    incident.status = STATUS_CLOSED
    return incident


def reopen_incident(incident: Incident) -> Incident:
    if incident.status not in {
        STATUS_VERIFICATION_PENDING,
        "RESOLVED",
    }:
        raise ValueError(
            "Only a resolved or verification-pending incident can be reopened."
        )

    incident.reopened_count += 1
    incident.status = STATUS_REOPENED
    incident.verified_at = None
    return incident
