from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.role import Role
from app.models.user import User
from app.auth import get_current_user


router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)


@router.get("")
def get_roles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    roles = (
        db.query(Role)
        .order_by(Role.id)
        .all()
    )

    return roles


@router.get("/{role_id}")
def get_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    role = (
        db.query(Role)
        .filter(Role.id == role_id)
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=404,
            detail="Role not found"
        )

    return role