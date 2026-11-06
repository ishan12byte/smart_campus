from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.auth import get_current_user
from app.services.decision_engine_adapter import run_decision_engine

from app.models.user import User
from app.models.incident import (
    Incident,
    IncidentReport,
    IncidentActionHistory,
)

from app.schemas import (
    IncidentCreate,
    IncidentResponse,
    IncidentReportResponse,
    IncidentActionHistoryResponse,
    IncidentActionRequest,
)

from app.rbac import (
    filter_incidents_for_user,
    get_visible_incident,
    get_user_role,
)

router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"],
)


@router.get(
    "/{incident_id}/history",
    response_model=list[IncidentActionHistoryResponse],
)
def get_incident_history(
    incident_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Confirm the user is allowed to view this incident.
    incident = get_visible_incident(
        incident_id,
        current_user,
        db,
    )

    return (
        db.query(IncidentActionHistory)
        .filter(
            IncidentActionHistory.incident_id == incident.id
        )
        .order_by(IncidentActionHistory.created_at.asc())
        .all()
    )


@router.post(
    "/{incident_id}/action/{action}",
    response_model=IncidentResponse,
)
def perform_incident_action(
    incident_id: int,
    action: str,
    action_data: IncidentActionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Perform an authorized incident lifecycle action.
    Every successful action creates an audit-history record.
    """

    allowed_transitions = {
        "acknowledge": ("REPORTED", "ACKNOWLEDGED"),
        "start": (("ACKNOWLEDGED", "REOPENED"), "IN_PROGRESS"),
        "resolve": ("IN_PROGRESS", "RESOLVED"),
        "verify": ("RESOLVED", "VERIFIED"),
        "reopen": (("RESOLVED", "VERIFIED"), "REOPENED"),
    }

    if action not in allowed_transitions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported incident action",
        )

    # Check incident visibility first.
    incident = get_visible_incident(
        incident_id,
        current_user,
        db,
    )

    role_name = get_user_role(current_user, db)

    # --------------------------------------------------------
    # AUTHORIZATION
    # --------------------------------------------------------

    is_admin = role_name == "SUPER_ADMIN"

    is_department_head = (
        role_name == "DEPARTMENT_HEAD"
        and incident.responsible_department_id
        == current_user.department_id
    )

    is_assigned_staff = (
        role_name == "STAFF"
        and incident.assigned_to_id == current_user.id
    )

    is_department_staff = (
        role_name == "STAFF"
        and incident.responsible_department_id
        == current_user.department_id
    )

    is_reporting_student = (
        role_name == "STUDENT"
        and db.query(IncidentReport.id)
        .filter(
            IncidentReport.incident_id == incident.id,
            IncidentReport.reported_by == current_user.id,
        )
        .first()
        is not None
    )

    if action in ("acknowledge", "start", "resolve"):

        staff_can_handle = (
            is_assigned_staff
            or (
                action == "acknowledge"
                and is_department_staff
                and incident.assigned_to_id is None
            )
        )

        if not (
            is_admin
            or is_department_head
            or staff_can_handle
        ):
            raise HTTPException(
                status_code=403,
                detail="You cannot perform this staff action",
            )

    elif action in ("verify", "reopen"):

        if not (
            is_admin
            or is_department_head
            or is_reporting_student
        ):
            raise HTTPException(
                status_code=403,
                detail="You cannot verify or reopen this incident",
            )

    # --------------------------------------------------------
    # VALIDATE STATUS TRANSITION
    # --------------------------------------------------------

    previous_status = incident.status
    allowed_previous, new_status = allowed_transitions[action]

    if isinstance(allowed_previous, str):
        allowed_previous = (allowed_previous,)

    if previous_status not in allowed_previous:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Cannot perform '{action}' while incident "
                f"status is '{previous_status}'"
            ),
        )

    now = datetime.now(timezone.utc)

    # --------------------------------------------------------
    # APPLY ACTION
    # --------------------------------------------------------

    incident.status = new_status

    if action == "acknowledge":
        incident.acknowledged_at = now

        # A staff member claiming an unassigned departmental
        # incident becomes its assigned staff member.
        if role_name == "STAFF" and incident.assigned_to_id is None:
            incident.assigned_to_id = current_user.id
            incident.assigned_resource_name = current_user.name

    elif action == "start":
        incident.started_at = now

    elif action == "resolve":
        incident.resolved_at = now

    elif action == "verify":
        incident.verified_at = now

    elif action == "reopen":
        incident.reopened_count += 1
        incident.started_at = None
        incident.resolved_at = None
        incident.verified_at = None

    # --------------------------------------------------------
    # SAVE AUDIT HISTORY
    # --------------------------------------------------------

    history = IncidentActionHistory(
        incident_id=incident.id,
        actor_user_id=current_user.id,
        action=action.upper(),
        previous_status=previous_status,
        new_status=new_status,
        note=action_data.note,
    )

    try:
        db.add(history)
        db.commit()
        db.refresh(incident)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to update incident lifecycle",
        )

    return incident

# ============================================================
# CREATE INCIDENT
# ============================================================

@router.post(
    "",
    response_model=IncidentResponse,
    status_code=201,
)
def create_incident(
    incident_data: IncidentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Process a submission through the Decision Engine.

    A recurring submission is attached to its existing incident.
    A new issue creates a new incident.
    Every submission is preserved as an individual report.
    """

    try:
        result, department, category_key, subcategory = (
            run_decision_engine(db, incident_data, current_user)
        )

        # Find the existing database incident if recurrence was detected.
        if result.is_new_incident:
            incident = Incident(
                title=incident_data.title,
                description=incident_data.description,
                category=category_key,
                subcategory=subcategory,
                location=incident_data.location,
                reported_by=current_user.id,
                impact=incident_data.impact,
                urgency=incident_data.urgency,
                safety=incident_data.safety,
                deadline=incident_data.deadline,
                recurrence=incident_data.recurrence,
                incident_type=incident_data.incident_type,
                evidence_available=incident_data.evidence_available,
                session_id=incident_data.session_id,
                service_cycle_id=incident_data.service_cycle_id,
                sla_deadline=incident_data.sla_deadline,
                status="REPORTED",
            )
            db.add(incident)
            db.flush()
        else:
            incident = (
                db.query(Incident)
                .filter(Incident.id == result.incident.id)
                .with_for_update()
                .first()
            )

            if incident is None:
                raise HTTPException(
                    status_code=409,
                    detail="The matching incident no longer exists. Please retry.",
                )

        # Save the Decision Engine outputs on the main incident.
        incident.responsible_department_id = department.id
        incident.priority_score = result.priority["score"]
        incident.priority_level = result.priority["level"]
        incident.responsibility_status = result.responsibility["status"]

        resource = result.assignment.resource

        # Preserve the existing assignee for recurring incidents.
        if incident.assigned_to_id is None and resource:
            incident.assigned_to_id = resource.id
            incident.assigned_resource_name = resource.name

        incident.escalation_level = result.escalation.level
        incident.escalation_reason = result.escalation.reason

        # Preserve every individual submission.
        report = IncidentReport(
            incident_id=incident.id,
            reported_by=current_user.id,
            title=incident_data.title,
            description=incident_data.description,
            category=category_key,
            subcategory=subcategory,
            location=incident_data.location,
            impact=incident_data.impact,
            urgency=incident_data.urgency,
            safety=incident_data.safety,
            deadline=incident_data.deadline,
            recurrence=incident_data.recurrence,
            incident_type=incident_data.incident_type,
            evidence_available=incident_data.evidence_available,
            session_id=incident_data.session_id,
            service_cycle_id=incident_data.service_cycle_id,
        )

        db.add(report)
        db.commit()
        db.refresh(incident)

        return incident

    except HTTPException:
        db.rollback()
        raise

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Incident could not be processed and saved.",
        )


# ============================================================
# GET ALL VISIBLE INCIDENTS
# ============================================================

@router.get(
    "",
    response_model=list[IncidentResponse],
)
def get_incidents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return incidents according to role and department access.
    """

    query = db.query(Incident)

    query = filter_incidents_for_user(
        query,
        current_user,
        db,
    )

    incidents = (
        query
        .order_by(
            Incident.created_at.desc(),
            Incident.id.desc(),
        )
        .all()
    )

    return incidents


# ============================================================
# GET REPORT HISTORY FOR ONE INCIDENT
# ============================================================

@router.get(
    "/{incident_id}/reports",
    response_model=list[IncidentReportResponse],
)
def get_incident_reports(
    incident_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve individual submissions linked to an incident.

    Students can see only their own individual reports.
    Other permitted roles can see the reports for incidents
    they are authorized to access.
    """

    incident = get_visible_incident(
        incident_id,
        current_user,
        db,
    )

    query = (
        db.query(IncidentReport)
        .filter(IncidentReport.incident_id == incident.id)
    )

    role_name = get_user_role(current_user, db)

    if role_name == "STUDENT":
        query = query.filter(
            IncidentReport.reported_by == current_user.id
        )

    return (
        query
        .order_by(IncidentReport.reported_at.asc())
        .all()
    )


# ============================================================
# GET ONE INCIDENT
# ============================================================

@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
)
def get_incident(
    incident_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve an individual incident using shared visibility rules.
    """

    return get_visible_incident(
        incident_id,
        current_user,
        db,
    )
