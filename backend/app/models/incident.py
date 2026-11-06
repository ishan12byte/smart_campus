
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.sql import func

from app.database import Base


class Incident(Base):
    """
    Main incident record.
    Represents the ongoing issue, not an individual student submission.
    """

    __tablename__ = "incidents"

    __table_args__ = (
        CheckConstraint(
            "impact BETWEEN 1 AND 5",
            name="ck_incidents_impact_range",
        ),
        CheckConstraint(
            "urgency BETWEEN 1 AND 5",
            name="ck_incidents_urgency_range",
        ),
        CheckConstraint(
            "safety BETWEEN 1 AND 5",
            name="ck_incidents_safety_range",
        ),
        CheckConstraint(
            "deadline BETWEEN 1 AND 5",
            name="ck_incidents_deadline_range",
        ),
        CheckConstraint(
            "recurrence BETWEEN 1 AND 5",
            name="ck_incidents_recurrence_range",
        ),
        CheckConstraint(
            "reopened_count >= 0",
            name="ck_incidents_reopened_count",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    # Basic incident details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    subcategory = Column(String, nullable=True)
    location = Column(String, nullable=False)

    responsible_department_id = Column(
    Integer,
    ForeignKey(
        "departments.id",
        name="fk_incidents_responsible_department_id_departments",
    ),
    nullable=True,
    index=True,
    )

    reported_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # Decision Engine input fields
    impact = Column(
        Integer, nullable=False, default=3, server_default=text("3")
    )
    urgency = Column(
        Integer, nullable=False, default=3, server_default=text("3")
    )
    safety = Column(
        Integer, nullable=False, default=3, server_default=text("3")
    )
    deadline = Column(
        Integer, nullable=False, default=3, server_default=text("3")
    )
    recurrence = Column(
        Integer, nullable=False, default=1, server_default=text("1")
    )

    incident_type = Column(String, nullable=True)
    evidence_available = Column(
        Boolean, nullable=False, default=False,
        server_default=text("false"),
    )

    session_id = Column(String, nullable=True)
    service_cycle_id = Column(String, nullable=True)

    # Decision Engine output fields
    priority_score = Column(Float, nullable=True)
    priority_level = Column(String, nullable=True)

    assigned_to_id = Column(
    Integer,
    ForeignKey(
        "users.id",
        name="fk_incidents_assigned_to_id_users",
    ),
    nullable=True,
    index=True,
    )
    assigned_resource_name = Column(String, nullable=True)

    escalation_level = Column(
        String,
        nullable=False,
        default="NONE",
        server_default=text("'NONE'"),
    )
    escalation_reason = Column(Text, nullable=True)
    responsibility_status = Column(String, nullable=True)

    # Lifecycle fields
    status = Column(
        String,
        nullable=False,
        default="REPORTED",
        server_default=text("'REPORTED'"),
    )

    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    reopened_count = Column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )

    # Actual SLA deadline timestamp.
    # This is different from the numeric deadline priority input above.
    sla_deadline = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class IncidentReport(Base):
    """
    One record for every individual incident submission.

    Multiple reports can be linked to the same ongoing incident.
    """

    __tablename__ = "incident_reports"

    id = Column(Integer, primary_key=True, index=True)

    incident_id = Column(
        Integer,
        ForeignKey("incidents.id"),
        nullable=False,
        index=True,
    )

    reported_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )


    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    subcategory = Column(String, nullable=True)
    location = Column(String, nullable=False)

    impact = Column(Integer, nullable=False)
    urgency = Column(Integer, nullable=False)
    safety = Column(Integer, nullable=False)
    deadline = Column(Integer, nullable=False)
    recurrence = Column(Integer, nullable=False)

    incident_type = Column(String, nullable=True)
    evidence_available = Column(Boolean, nullable=False, default=False)

    session_id = Column(String, nullable=True)
    service_cycle_id = Column(String, nullable=True)

    reported_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class IncidentActionHistory(Base):
    """
    Audit trail for every lifecycle action performed on an incident.
    """

    __tablename__ = "incident_action_history"

    id = Column(Integer, primary_key=True, index=True)

    incident_id = Column(
        Integer,
        ForeignKey("incidents.id"),
        nullable=False,
        index=True,
    )

    actor_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    action = Column(String, nullable=False)
    previous_status = Column(String, nullable=False)
    new_status = Column(String, nullable=False)
    note = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
