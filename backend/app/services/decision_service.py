from datetime import datetime
from sqlalchemy.orm import Session

from app.models.incident import Incident as DBIncident
from app.models.user import User
from app.models.role import Role
from app.models.department import Department
from app.schemas import IncidentCreate

from decision_engine.models import Report, Incident as DEIncident
from decision_engine.workload import Resource
from decision_engine.engine import (
    DecisionInput,
    PriorityInput,
    ResponsibilityInput,
    process_decision,
)
from decision_engine.lifecycle import (
    acknowledge_incident,
    start_incident,
    mark_resolved,
    verify_resolution,
    reopen_incident,
)
from decision_engine.escalation import determine_escalation
from decision_engine.categories import CATEGORIES


def get_categories_metadata() -> dict:
    """Return available campus incident categories and subcategories."""
    return CATEGORIES


def map_db_to_de_incident(db_inc: DBIncident) -> DEIncident:
    """Convert SQLAlchemy Incident model to Decision Engine dataclass."""
    return DEIncident(
        id=db_inc.id,
        category=db_inc.category,
        subcategory=db_inc.subcategory or "",
        location=db_inc.location,
        started_at=db_inc.created_at or datetime.now(),
        status=db_inc.status,
        report_ids=[db_inc.id],
        resolved_at=db_inc.resolved_at,
        verified_at=db_inc.verified_at,
        reopened_count=db_inc.reopened_count or 0,
        session_id=db_inc.session_id,
        service_cycle_id=db_inc.service_cycle_id,
    )


def load_resources_from_db(db: Session) -> list[Resource]:
    """Load active staff resources and their current assigned hours from DB."""
    staff_roles = db.query(Role).filter(Role.name.in_(["STAFF", "DEPARTMENT_HEAD"])).all()
    role_ids = [r.id for r in staff_roles]

    staff_users = (
        db.query(User)
        .filter(User.role_id.in_(role_ids), User.is_active == True)
        .all()
    )

    departments_map = {d.id: d.code for d in db.query(Department).all()}

    resources: list[Resource] = []
    for staff in staff_users:
        dept_code = departments_map.get(staff.department_id, "ADMINISTRATION")
        # Calculate currently active assigned hours (each active incident = 1.0 hour)
        active_assigned_count = (
            db.query(DBIncident)
            .filter(
                DBIncident.assigned_to_id == staff.id,
                DBIncident.status.in_(["ASSIGNED", "IN_PROGRESS", "ACKNOWLEDGED", "REPORTED"]),
            )
            .count()
        )
        resources.append(
            Resource(
                id=staff.id,
                name=staff.name,
                department=dept_code,
                capacity_hours=8.0,
                assigned_hours=float(active_assigned_count * 1.5),
            )
        )

    # If no staff user is present in a category, provide default departmental virtual resources
    if not resources:
        for dept_id, dept_code in departments_map.items():
            resources.append(
                Resource(
                    id=dept_id + 1000,
                    name=f"{dept_code} Operations Lead",
                    department=dept_code,
                    capacity_hours=8.0,
                    assigned_hours=0.0,
                )
            )

    return resources


def process_new_incident_submission(
    incident_data: IncidentCreate,
    current_user: User,
    db: Session
) -> DBIncident:
    """Execute decision engine pipeline on newly submitted incident report."""
    # 1. Fetch active incidents from DB for recurrence detection
    active_db_incidents = (
        db.query(DBIncident)
        .filter(DBIncident.status.notin_(["CLOSED", "RESOLVED"]))
        .all()
    )
    de_incidents = [map_db_to_de_incident(inc) for inc in active_db_incidents]

    # 2. Fetch available resources
    resources = load_resources_from_db(db)

    # 3. Determine next incident ID
    max_id = db.query(DBIncident.id).order_by(DBIncident.id.desc()).first()
    next_id = (max_id[0] + 1) if max_id else 1

    # 4. Build Report
    subcategory = incident_data.subcategory or "GENERAL"
    report = Report(
        id=next_id,
        description=incident_data.description,
        category=incident_data.category.upper().strip(),
        subcategory=subcategory.upper().strip(),
        location=incident_data.location.strip(),
        reported_at=datetime.now(),
        reporter_id=current_user.id,
        session_id=incident_data.session_id,
        service_cycle_id=incident_data.service_cycle_id,
    )

    # 5. Build Decision Inputs
    priority_input = PriorityInput(
        impact=max(1, min(5, incident_data.impact)),
        urgency=max(1, min(5, incident_data.urgency)),
        safety=max(1, min(5, incident_data.safety)),
        deadline=max(1, min(5, incident_data.deadline)),
        recurrence=max(1, min(5, incident_data.recurrence)),
        incident_type=incident_data.incident_type,
    )

    responsibility_input = ResponsibilityInput(
        evidence_available=incident_data.evidence_available,
        department_expected_to_handle=True,
    )

    decision_input = DecisionInput(
        report=report,
        incidents=de_incidents,
        resources=resources,
        new_incident_id=next_id,
        priority=priority_input,
        responsibility=responsibility_input,
        required_hours=1.5,
    )

    # 6. Execute deterministic Decision Engine
    decision_result = process_decision(decision_input)

    # 7. Persist or update incident in DB
    assigned_user_id = None
    assigned_name = None
    if decision_result.assignment.assigned and decision_result.assignment.resource:
        res = decision_result.assignment.resource
        assigned_name = res.name
        # Check if resource ID corresponds to an actual DB User
        user_match = db.query(User).filter(User.id == res.id).first()
        if user_match:
            assigned_user_id = user_match.id

    if decision_result.is_new_incident:
        new_incident = DBIncident(
            title=incident_data.title,
            description=incident_data.description,
            category=incident_data.category.upper().strip(),
            subcategory=subcategory.upper().strip(),
            location=incident_data.location.strip(),
            reported_by=current_user.id,
            status="REPORTED",
            priority_score=decision_result.priority.get("score"),
            priority_level=decision_result.priority.get("level", "LOW"),
            assigned_to_id=assigned_user_id,
            assigned_resource_name=assigned_name,
            escalation_level=decision_result.escalation.level,
            escalation_reason=decision_result.escalation.reason,
            responsibility_status=decision_result.responsibility.get("status"),
            session_id=incident_data.session_id,
            service_cycle_id=incident_data.service_cycle_id,
            reopened_count=0,
        )
        db.add(new_incident)
        db.commit()
        db.refresh(new_incident)
        return new_incident
    else:
        # Match found: link to existing incident
        existing_db_incident = (
            db.query(DBIncident)
            .filter(DBIncident.id == decision_result.incident.id)
            .first()
        )
        if existing_db_incident:
            existing_db_incident.priority_score = decision_result.priority.get("score")
            existing_db_incident.priority_level = decision_result.priority.get("level", existing_db_incident.priority_level)
            existing_db_incident.escalation_level = decision_result.escalation.level
            existing_db_incident.escalation_reason = decision_result.escalation.reason
            db.commit()
            db.refresh(existing_db_incident)
            return existing_db_incident

        # Fallback if ID mismatch
        new_incident = DBIncident(
            title=incident_data.title,
            description=incident_data.description,
            category=incident_data.category.upper().strip(),
            subcategory=subcategory.upper().strip(),
            location=incident_data.location.strip(),
            reported_by=current_user.id,
            status="REPORTED",
            priority_score=decision_result.priority.get("score"),
            priority_level=decision_result.priority.get("level", "LOW"),
            assigned_to_id=assigned_user_id,
            assigned_resource_name=assigned_name,
            escalation_level=decision_result.escalation.level,
            escalation_reason=decision_result.escalation.reason,
            responsibility_status=decision_result.responsibility.get("status"),
        )
        db.add(new_incident)
        db.commit()
        db.refresh(new_incident)
        return new_incident


def advance_incident_lifecycle(
    incident_id: int,
    action: str,
    current_user: User,
    db: Session
) -> DBIncident:
    """Advance incident lifecycle using decision engine transition rules."""
    db_incident = db.query(DBIncident).filter(DBIncident.id == incident_id).first()
    if not db_incident:
        raise ValueError("Incident not found")

    de_incident = map_db_to_de_incident(db_incident)

    action = action.lower().strip()
    if action == "acknowledge":
        acknowledge_incident(de_incident)
    elif action == "start":
        start_incident(de_incident)
    elif action == "resolve":
        mark_resolved(de_incident)
    elif action == "verify":
        verify_resolution(de_incident)
    elif action == "reopen":
        reopen_incident(de_incident)
    else:
        raise ValueError(f"Unknown lifecycle action: {action}")

    # Synchronize back to DB model
    db_incident.status = de_incident.status
    db_incident.resolved_at = de_incident.resolved_at
    db_incident.verified_at = de_incident.verified_at
    db_incident.reopened_count = de_incident.reopened_count

    # Check for escalation triggers based on reopened count or status
    escalation_res = determine_escalation(
        priority_level=db_incident.priority_level or "LOW",
        assignment_successful=db_incident.assigned_to_id is not None or db_incident.assigned_resource_name is not None,
        reopened_count=db_incident.reopened_count,
    )
    if escalation_res.escalated:
        db_incident.escalation_level = escalation_res.level
        db_incident.escalation_reason = escalation_res.reason

    db.commit()
    db.refresh(db_incident)
    return db_incident
