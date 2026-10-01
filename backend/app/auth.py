from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.security import hash_password, verify_password
from app.schemas import RegisterRequest, LoginRequest

from app.jwt_utils import create_access_token, decode_access_token


security = HTTPBearer()

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])

    except (ValueError, KeyError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )

    return user


@router.post("/register")
def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    # Check whether email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash the password before storing it
    hashed_password = hash_password(user_data.password)

    # Create new user
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password,
        role_id=user_data.role_id,
        department_id=user_data.department_id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id
    }


@router.post("/login")
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    # Find user by email
    user = (
        db.query(User)
        .filter(User.email == login_data.email)
        .first()
    )

    # Check whether user exists
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(
        login_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create JWT
    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role_id": current_user.role_id,
        "department_id": current_user.department_id,
        "is_active": current_user.is_active
    }