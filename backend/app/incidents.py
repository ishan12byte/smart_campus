from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.incident import Incident
from app.models.role import Role
from app.models.user import User
from app.schemas import IncidentCreate, IncidentResponse
from app.auth import get_current_user


router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"]
)


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
    new_incident = Incident(
        title=incident_data.title,
        description=incident_data.description,
        category=incident_data.category,
        subcategory=incident_data.subcategory,
        location=incident_data.location,
        reported_by=current_user.id
    )

    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)

    return new_incident


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
    else:
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