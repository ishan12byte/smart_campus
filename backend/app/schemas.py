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