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


class IncidentResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    subcategory: str | None
    location: str
    reported_by: int
    status: str
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
