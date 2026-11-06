
import os

os.environ.setdefault(
    "JWT_SECRET_KEY",
    "smart-campus-test-secret-key-123456789"
)
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.role import Role
from app.models.department import Department
from app.security import hash_password


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def test_data(db_session):
    role_names = [
        "STUDENT",
        "STAFF",
        "DEPARTMENT_HEAD",
        "SUPER_ADMIN",
    ]

    roles = {}
    for name in role_names:
        role = Role(name=name)
        db_session.add(role)
        roles[name] = role

    departments = {}
    department_data = [
        ("MAINTENANCE", "Maintenance"),
        ("IT", "IT"),
        ("SECURITY", "Security"),
        ("EXAMINATION", "Examination"),
        ("SANITATION", "Sanitation"),
        ("ADMINISTRATION", "Administration"),
        ("ACADEMIC_ADMIN", "Academic Administration"),
    ]

    for code, name in department_data:
        department = Department(
            code=code,
            name=name,
            is_active=True,
        )
        db_session.add(department)
        departments[code] = department

    db_session.flush()

    password = hash_password("TestPassword@123")

    users = {}
    user_data = [
        ("student", "student@test.com", "STUDENT", "IT"),
        ("staff", "staff@test.com", "STAFF", "MAINTENANCE"),
        ("head", "head@test.com", "DEPARTMENT_HEAD", "MAINTENANCE"),
        ("admin", "admin@test.com", "SUPER_ADMIN", "ADMINISTRATION"),
        ("other_student", "other@test.com", "STUDENT", "IT"),
    ]

    for key, email, role_name, department_code in user_data:
        user = User(
            name=key.title() + " Test",
            email=email,
            password_hash=password,
            role_id=roles[role_name].id,
            department_id=departments[department_code].id,
            is_active=True,
        )
        db_session.add(user)
        users[key] = user

    db_session.commit()

    for user in users.values():
        db_session.refresh(user)

    return {
        "users": users,
        "roles": roles,
        "departments": departments,
    }


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client, test_data):
    def get_headers(user_key):
        user = test_data["users"][user_key]

        response = client.post(
            "/auth/login",
            json={
                "email": user.email,
                "password": "TestPassword@123",
            },
        )

        assert response.status_code == 200

        token = response.json()["access_token"]

        return {"Authorization": f"Bearer {token}"}

    return get_headers
