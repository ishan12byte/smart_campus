from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from decision_engine.categories import CATEGORIES
from decision_engine.engine import (
    DecisionInput,
    PriorityInput,
    ResponsibilityInput,
    process_decision,
)
from decision_engine.models import Incident as EngineIncident
from decision_engine.models import Report
from decision_engine.workload import Resource

from app.models.department import Department
from app.models.user import User
from app.models.incident import Incident, IncidentReport


ACTIVE_STATUSES = {
    "REPORTED",
    "ACKNOWLEDGED",
    "UNDER_REVIEW",
    "ASSIGNED",
    "IN_PROGRESS",
    "REOPENED",
    "VERIFICATION_PENDING",
}

DEFAULT_CAPACITY_HOURS = 8.0
DEFAULT_REQUIRED_HOURS = 1.0


def normalize_category(category: str) -> str:
    value = category.strip().upper()

    for key, details in CATEGORIES.items():
        if value == key or value == details["name"].strip().upper():
            return key

    raise HTTPException(
        status_code=422,
        detail=f"Unsupported incident category: {category}",
    )


def validate_subcategory(category_key: str, subcategory: str | None) -> str:
    if not subcategory:
        raise HTTPException(
            status_code=422,
            detail="A subcategory is required for Decision Engine processing.",
        )

    value = subcategory.strip().upper()

    allowed = CATEGORIES[category_key]["subcategories"]

    if value not in allowed:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Invalid subcategory '{subcategory}' for "
                f"category '{category_key}'. Allowed values: {allowed}"
            ),
        )

    return value


def get_department(db: Session, category_key: str) -> Department:
    department_name = CATEGORIES[category_key]["name"]

    department = (
        db.query(Department)
        .filter(
            Department.is_active.is_(True),
            (
                Department.code.ilike(category_key)
                | Department.name.ilike(department_name)
            ),
        )
        .first()
    )

    if department is None:
        raise HTTPException(
            status_code=422,
            detail=f"No active department is configured for {department_name}.",
        )

    return department


def run_decision_engine(
    db: Session,
    incident_data,
    reporter: User,
):
    category_key = normalize_category(incident_data.category)
    subcategory = validate_subcategory(
        category_key,
        incident_data.subcategory,
    )

    department = get_department(db, category_key)
    now = datetime.now(timezone.utc)

    # Load existing incidents for recurrence matching.
    existing_incidents = (
        db.query(Incident)
        .filter(Incident.status.in_(ACTIVE_STATUSES))
        .all()
    )

    existing_reports = (
        db.query(IncidentReport)
        .filter(
            IncidentReport.incident_id.in_(
                [item.id for item in existing_incidents]
            )
        )
        .all()
        if existing_incidents
        else []
    )

    report_ids_by_incident = {}

    for item in existing_reports:
        report_ids_by_incident.setdefault(
            item.incident_id, []
        ).append(item.id)

    engine_incidents = []

    for item in existing_incidents:
        # Ignore legacy or placeholder records that do not use
        # categories supported by the Decision Engine.
        try:
            existing_category = normalize_category(item.category)
            existing_subcategory = validate_subcategory(
                existing_category,
                item.subcategory,
            )
        except HTTPException:
            continue

        engine_incidents.append(
            EngineIncident(
                id=item.id,
                category=existing_category,
                subcategory=existing_subcategory,
                location=item.location,
                started_at=item.started_at or item.created_at or now,
                status=item.status,
                report_ids=report_ids_by_incident.get(item.id, []),
                resolved_at=item.resolved_at,
                verified_at=item.verified_at,
                reopened_count=item.reopened_count,
                session_id=item.session_id,
                service_cycle_id=item.service_cycle_id,
            )
        )

    # Build workload resources for active staff in this department.
    staff_members = (
        db.query(User)
        .filter(
            User.department_id == department.id,
            User.is_active.is_(True),
        )
        .all()
    )

    resources = []

    for staff in staff_members:
        active_assignment_count = (
            db.query(Incident)
            .filter(
                Incident.assigned_to_id == staff.id,
                Incident.status.in_(ACTIVE_STATUSES),
            )
            .count()
        )

        resources.append(
            Resource(
                id=staff.id,
                name=staff.name,
                department=category_key,
                capacity_hours=DEFAULT_CAPACITY_HOURS,
                assigned_hours=(
                    active_assignment_count * DEFAULT_REQUIRED_HOURS
                ),
            )
        )

    # Negative temporary ID: the database generates the real report ID.
    engine_report = Report(
        id=-1,
        description=incident_data.description,
        category=category_key,
        subcategory=subcategory,
        location=incident_data.location,
        reported_at=now,
        reporter_id=reporter.id,
        session_id=incident_data.session_id,
        service_cycle_id=incident_data.service_cycle_id,
    )

    decision_input = DecisionInput(
        report=engine_report,
        incidents=engine_incidents,
        resources=resources,
        new_incident_id=-1,
        priority=PriorityInput(
            impact=incident_data.impact,
            urgency=incident_data.urgency,
            safety=incident_data.safety,
            deadline=incident_data.deadline,
            recurrence=incident_data.recurrence,
            incident_type=incident_data.incident_type,
        ),
        responsibility=ResponsibilityInput(
            evidence_available=incident_data.evidence_available,
        ),
        required_hours=DEFAULT_REQUIRED_HOURS,
        sla_deadline=incident_data.sla_deadline,
        reference_time=now,
    )

    result = process_decision(decision_input)

    return result, department, category_key, subcategory
