from datetime import datetime, timedelta
from decision_engine.models import Report, Incident
from decision_engine.recurrence import (
    is_candidate_match,
    find_matching_incident,
)

def test_multiple_reports_same_incident():

    start_time = datetime(2026, 8, 31, 10, 0)

    incident = Incident(
        id=101,
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        started_at=start_time,
        status="IN_PROGRESS",
        report_ids=[1],
    )

    second_report = Report(
        id=2,
        description="Projector in Room 203 is broken",
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        reported_at=start_time + timedelta(minutes=10),
        reporter_id=102,
    )

    assert is_candidate_match(second_report, incident) is True

def test_different_location_is_new_occurrence():

    start_time = datetime(2026, 8, 31, 10, 0)

    incident = Incident(
        id=101,
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        started_at=start_time,
        status="IN_PROGRESS",
        report_ids=[1],
    )

    report = Report(
        id=2,
        description="Projector is broken",
        category="IT",
        subcategory="PROJECTOR",
        location="Room 204",
        reported_at=start_time + timedelta(minutes=10),
        reporter_id=102,
    )

    assert is_candidate_match(report, incident) is False

def test_resolved_incident_is_not_candidate():

    start_time = datetime(2026, 8, 31, 10, 0)

    incident = Incident(
        id=101,
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        started_at=start_time,
        status="RESOLVED",
        report_ids=[1],
    )

    report = Report(
        id=2,
        description="Projector is broken again",
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        reported_at=start_time + timedelta(minutes=10),
        reporter_id=102,
    )

    assert is_candidate_match(report, incident) is False

def test_different_category_is_not_match():

    start_time = datetime(2026, 8, 31, 10, 0)

    incident = Incident(
        id=101,
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        started_at=start_time,
        status="IN_PROGRESS",
        report_ids=[1],
    )

    report = Report(
        id=2,
        description="Electricity problem",
        category="MAINTENANCE",
        subcategory="ELECTRICAL",
        location="Room 203",
        reported_at=start_time + timedelta(minutes=5),
        reporter_id=102,
    )

    assert is_candidate_match(report, incident) is False

def test_persistent_incident_can_match_report_after_several_hours():
    start_time = datetime(2026, 8, 31, 10, 0)

    incident = Incident(
        id=101,
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        started_at=start_time,
        status="IN_PROGRESS",
        report_ids=[1],
    )

    report = Report(
        id=2,
        description="Projector is still broken",
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        reported_at=start_time + timedelta(hours=6),
        reporter_id=102,
    )

    assert is_candidate_match(report, incident) is True

def test_find_matching_incident_returns_matching_incident():
    start_time = datetime(2026, 8, 31, 10, 0)

    incident = Incident(
        id=101,
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        started_at=start_time,
        status="IN_PROGRESS",
        report_ids=[1],
    )

    report = Report(
        id=2,
        description="Projector is still broken",
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        reported_at=start_time + timedelta(hours=5),
        reporter_id=102,
    )

    result = find_matching_incident(
        report,
        [incident],
    )

    assert result is incident

def test_find_matching_incident_selects_correct_incident():
    start_time = datetime(2026, 8, 31, 10, 0)

    projector_room_203 = Incident(
        id=101,
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        started_at=start_time,
        status="IN_PROGRESS",
        report_ids=[1],
    )

    projector_room_204 = Incident(
        id=102,
        category="IT",
        subcategory="PROJECTOR",
        location="Room 204",
        started_at=start_time,
        status="IN_PROGRESS",
        report_ids=[2],
    )

    network_room_203 = Incident(
        id=103,
        category="IT",
        subcategory="NETWORK",
        location="Room 203",
        started_at=start_time,
        status="IN_PROGRESS",
        report_ids=[3],
    )

    report = Report(
        id=4,
        description="Projector in Room 203 is still broken",
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        reported_at=start_time + timedelta(hours=6),
        reporter_id=102,
    )

    result = find_matching_incident(
        report,
        [
            projector_room_204,
            network_room_203,
            projector_room_203,
        ],
    )

    assert result is projector_room_203