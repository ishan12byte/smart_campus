
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============================================================
# AUTHENTICATION SCHEMAS
# ============================================================

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    department_id: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ============================================================
# INCIDENT INPUT SCHEMA
# Data received from the frontend
# ============================================================

class IncidentCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    # Basic incident details
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    category: str = Field(min_length=1)
    subcategory: str | None = None
    location: str = Field(min_length=1)

    # Decision Engine input fields (1-5)
    impact: int = Field(default=3, ge=1, le=5)
    urgency: int = Field(default=3, ge=1, le=5)
    safety: int = Field(default=3, ge=1, le=5)
    deadline: int = Field(default=3, ge=1, le=5)
    recurrence: int = Field(default=1, ge=1, le=5)

    # Additional incident information
    incident_type: str | None = None
    evidence_available: bool = False

    session_id: str | None = None
    service_cycle_id: str | None = None

    # Actual deadline timestamp, separate from
    # the numeric deadline priority input above.
    sla_deadline: datetime | None = None


# ============================================================
# INCIDENT RESPONSE SCHEMA
# Data returned to the frontend
# ============================================================

class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    # Basic details
    title: str
    description: str
    category: str
    subcategory: str | None
    location: str
    reported_by: int
    responsible_department_id: int | None

    # Decision Engine input fields
    impact: int
    urgency: int
    safety: int
    deadline: int
    recurrence: int

    incident_type: str | None
    evidence_available: bool
    session_id: str | None
    service_cycle_id: str | None

    # Decision Engine output fields
    priority_score: float | None
    priority_level: str | None

    assigned_to_id: int | None
    assigned_resource_name: str | None

    escalation_level: str
    escalation_reason: str | None
    responsibility_status: str | None

    # Lifecycle information
    status: str

    acknowledged_at: datetime | None
    started_at: datetime | None
    resolved_at: datetime | None
    verified_at: datetime | None

    reopened_count: int
    sla_deadline: datetime | None

    created_at: datetime
    updated_at: datetime


# ============================================================
# INCIDENT REPORT SCHEMAS
# One response for each individual submission
# ============================================================

class IncidentReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    reported_by: int

    title: str
    description: str
    category: str
    subcategory: str | None
    location: str

    impact: int
    urgency: int
    safety: int
    deadline: int
    recurrence: int

    incident_type: str | None
    evidence_available: bool

    session_id: str | None
    service_cycle_id: str | None

    reported_at: datetime


# ============================================================
# INCIDENT ACTION SCHEMAS
# ============================================================

class IncidentActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    note: str | None = None


class IncidentActionHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    actor_user_id: int

    action: str
    previous_status: str
    new_status: str
    note: str | None

    created_at: datetime


# ============================================================
# DEPARTMENT SCHEMAS
# ============================================================

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
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str | None
    is_active: bool

    created_at: datetime
    updated_at: datetime


# ============================================================
# USER RESPONSE SCHEMA
# ============================================================

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr

    role_id: int
    department_id: int
    is_active: bool

    created_at: datetime
