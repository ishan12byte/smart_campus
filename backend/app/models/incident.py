from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    description = Column(Text, nullable=False)

    category = Column(String, nullable=False)

    subcategory = Column(String, nullable=True)

    location = Column(String, nullable=False)

    reported_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    status = Column(
        String,
        default="REPORTED",
        nullable=False
    )

    priority_score = Column(Float, nullable=True)
    priority_level = Column(String, default="LOW", nullable=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_resource_name = Column(String, nullable=True)
    escalation_level = Column(String, default="NONE", nullable=False)
    escalation_reason = Column(Text, nullable=True)
    responsibility_status = Column(String, nullable=True)
    session_id = Column(String, nullable=True)
    service_cycle_id = Column(String, nullable=True)
    reopened_count = Column(Integer, default=0, nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )