from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.role import Role
from app.models.user import User
from app.auth import get_current_user


def require_roles(*allowed_roles):
    def role_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
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

        if role.name not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action"
            )

        return current_user

    return role_checker