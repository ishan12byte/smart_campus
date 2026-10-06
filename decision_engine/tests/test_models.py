from datetime import datetime, timedelta
from decision_engine.models import Report, Incident

def test_new_incident_has_no_resolution():
    incident = Incident(
        id=101,
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        started_at=datetime(2026, 8, 31, 10, 0),
        status="IN_PROGRESS",
        report_ids=[1],
    )

    assert incident.resolved_at is None
    assert incident.verified_at is None

def test_incident_can_store_resolved_at():
    resolved_time = datetime(2026, 8, 31, 12, 0)

    incident = Incident(
        id=101,
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        started_at=datetime(2026, 8, 31, 10, 0),
        status="RESOLVED",
        report_ids=[1],
        resolved_at=resolved_time,
    )

    assert incident.resolved_at == resolved_time
    assert incident.verified_at is None

def test_incident_can_store_verification_time():
    resolved_time = datetime(2026, 8, 31, 12, 0)
    verified_time = datetime(2026, 8, 31, 12, 30)

    incident = Incident(
        id=101,
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        started_at=datetime(2026, 8, 31, 10, 0),
        status="CLOSED",
        report_ids=[1],
        resolved_at=resolved_time,
        verified_at=verified_time,
    )

    assert incident.resolved_at == resolved_time
    assert incident.verified_at == verified_time

def test_report_can_store_session_context():
    report = Report(
        id=102,
        description="Exam hall issue",
        category="EXAMINATION",
        subcategory="HALL_ALLOCATION",
        location="Hall A",
        reported_at=datetime(2026, 8, 31, 10, 0),
        reporter_id=201,
        session_id="EXAM-2026-08-31-AM",
    )

    assert report.session_id == "EXAM-2026-08-31-AM"
    assert report.service_cycle_id is None


def test_report_can_store_service_cycle_context():
    report = Report(
        id=103,
        description="Cleaning issue",
        category="SANITATION",
        subcategory="CLEANING",
        location="Washroom A",
        reported_at=datetime(2026, 8, 31, 10, 0),
        reporter_id=202,
        service_cycle_id="CYCLE-100",
    )

    assert report.service_cycle_id == "CYCLE-100"
    assert report.session_id is None
