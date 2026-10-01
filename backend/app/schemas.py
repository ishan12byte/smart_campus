from datetime import datetime
from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role_id: int
    department_id: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class IncidentCreate(BaseModel):
    title: str
    description: str
    category: str
    subcategory: str | None = None
    location: str
    impact: int = 3
    urgency: int = 3
    safety: int = 3
    deadline: int = 3
    recurrence: int = 1
    incident_type: str | None = None
    session_id: str | None = None
    service_cycle_id: str | None = None
    evidence_available: bool = False


class IncidentResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    subcategory: str | None = None
    location: str
    reported_by: int
    status: str
    priority_score: float | None = None
    priority_level: str | None = None
    assigned_to_id: int | None = None
    assigned_resource_name: str | None = None
    escalation_level: str = "NONE"
    escalation_reason: str | None = None
    responsibility_status: str | None = None
    session_id: str | None = None
    service_cycle_id: str | None = None
    reopened_count: int = 0
    resolved_at: datetime | None = None
    verified_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class DepartmentCreate(BaseModel):
    code: str
    name: str
    description: str | None = None


class DepartmentUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class DepartmentResponse(BaseModel):
    id: int
    code: str
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role_id: int
    department_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
