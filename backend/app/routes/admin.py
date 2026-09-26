from fastapi import APIRouter, Depends

from app.models.user import User
from app.rbac import require_roles


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/test")
def admin_test(
    current_user: User = Depends(
        require_roles("ADMIN", "SUPER_ADMIN")
    )
):
    return {
        "message": "Admin access granted",
        "user_id": current_user.id,
        "name": current_user.name
    }