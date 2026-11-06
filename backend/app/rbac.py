
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.role import Role
from app.models.user import User
from app.models.incident import Incident, IncidentReport
from app.auth import get_current_user


# ============================================================
# ROLE-BASED ACCESS CONTROL
# ============================================================

def get_user_role(current_user: User, db: Session) -> str:
    """
    Return the logged-in user's role name.
    """

    role = (
        db.query(Role)
        .filter(Role.id == current_user.role_id)
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=403,
            detail="User role not found"
        )

    return role.name


def require_roles(*allowed_roles):
    """
    Restrict an endpoint to specific roles.
    """

    def role_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        role_name = get_user_role(current_user, db)

        if role_name not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action"
            )

        return current_user

    return role_checker


# ============================================================
# INCIDENT VISIBILITY
# ============================================================

def filter_incidents_for_user(
    query,
    current_user: User,
    db: Session
):
    """
    Apply incident visibility rules according to the user's role.

    STUDENT:
        Can see incidents they reported or individually reported on.

    STAFF:
        Can see incidents assigned to them or belonging
        to their responsible department.

    DEPARTMENT_HEAD:
        Can see incidents belonging to their department.

    SUPER_ADMIN:
        Can see all incidents.
    """

    role_name = get_user_role(current_user, db)

    # SUPER_ADMIN can see all incidents.
    if role_name == "SUPER_ADMIN":
        return query

    # STUDENT can see incidents they reported.
    # They can also see incidents they submitted an individual report for.
    if role_name == "STUDENT":
        reported_incident_ids = (
            db.query(IncidentReport.incident_id)
            .filter(
                IncidentReport.reported_by == current_user.id
            )
        )

        return query.filter(
            or_(
                Incident.reported_by == current_user.id,
                Incident.id.in_(reported_incident_ids)
            )
        )

    # STAFF can see incidents assigned to them
    # or belonging to their department.
    if role_name == "STAFF":
        return query.filter(
            or_(
                Incident.assigned_to_id == current_user.id,
                Incident.responsible_department_id
                == current_user.department_id
            )
        )

    # DEPARTMENT_HEAD can see incidents belonging to their department.
    if role_name == "DEPARTMENT_HEAD":
        return query.filter(
            Incident.responsible_department_id
            == current_user.department_id
        )

    raise HTTPException(
        status_code=403,
        detail="Your role cannot access incidents"
    )


# ============================================================
# SINGLE INCIDENT ACCESS
# ============================================================

def get_visible_incident(
    incident_id: int,
    current_user: User,
    db: Session
):
    """
    Get an incident only if the current user is permitted
    to view it.

    Returns 404 for both nonexistent and inaccessible incidents
    to avoid revealing records to unauthorized users.
    """

    query = db.query(Incident)

    query = filter_incidents_for_user(
        query,
        current_user,
        db
    )

    incident = (
        query
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    return incident
