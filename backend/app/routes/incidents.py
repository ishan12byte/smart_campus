from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.incident import Incident
from app.models.role import Role
from app.models.department import Department
from app.models.user import User
from app.schemas import IncidentCreate, IncidentResponse
from app.auth import get_current_user
from app.services.decision_service import (
    process_new_incident_submission,
    advance_incident_lifecycle,
    get_categories_metadata,
)


router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"]
)


@router.get("/categories")
def get_categories():
    """Return available categories and subcategories defined in decision engine."""
    return get_categories_metadata()


@router.post(
    "",
    response_model=IncidentResponse,
    status_code=201
)
def create_incident(
    incident_data: IncidentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        new_incident = process_new_incident_submission(
            incident_data=incident_data,
            current_user=current_user,
            db=db
        )
        return new_incident
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process incident: {str(exc)}"
        )


@router.get(
    "",
    response_model=list[IncidentResponse]
)
def get_incidents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    role = (
        db.query(Role)
        .filter(Role.id == current_user.role_id)
        .first()
    )

    if role and role.name == "STUDENT":
        incidents = (
            db.query(Incident)
            .filter(Incident.reported_by == current_user.id)
            .order_by(Incident.id.desc())
            .all()
        )
    elif role and role.name == "STAFF":
        # Staff can see incidents assigned directly to them or within their department category
        dept = db.query(Department).filter(Department.id == current_user.department_id).first()
        dept_code = dept.code if dept else None
        
        incidents = (
            db.query(Incident)
            .filter(
                (Incident.assigned_to_id == current_user.id) |
                (Incident.category == dept_code) |
                (Incident.assigned_to_id == None)
            )
            .order_by(Incident.id.desc())
            .all()
        )
    else:
        # Admins and department heads can see all incidents
        incidents = (
            db.query(Incident)
            .order_by(Incident.id.desc())
            .all()
        )

    return incidents


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse
)
def get_incident(
    incident_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    role = (
        db.query(Role)
        .filter(Role.id == current_user.role_id)
        .first()
    )

    if role and role.name == "STUDENT":
        if incident.reported_by != current_user.id:
            raise HTTPException(
                status_code=404,
                detail="Incident not found"
            )

    return incident


@router.post(
    "/{incident_id}/action/{action}",
    response_model=IncidentResponse
)
def handle_incident_action(
    incident_id: int,
    action: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        updated_incident = advance_incident_lifecycle(
            incident_id=incident_id,
            action=action,
            current_user=current_user,
            db=db
        )
        return updated_incident
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Lifecycle transition failed: {str(exc)}")