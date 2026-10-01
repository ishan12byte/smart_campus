from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    email = Column(String, unique=True, nullable=False, index=True)

    password_hash = Column(String, nullable=False)

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    department_id = Column(
        Integer,
        ForeignKey("departments.id"),
        nullable=False
    )

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())