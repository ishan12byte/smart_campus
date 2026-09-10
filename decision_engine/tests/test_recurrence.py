from datetime import datetime, timedelta
from decision_engine.models import Report, Incident
from decision_engine.recurrence import (
    is_candidate_match,
    find_matching_incident,
    attach_report_to_incident,
    create_incident,
    process_report,
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

def test_attach_report_to_incident():
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
        reported_at=start_time + timedelta(hours=4),
        reporter_id=102,
    )

    attach_report_to_incident(report, incident)

    assert incident.report_ids == [1, 2]

def test_same_report_is_not_attached_twice():
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
        reported_at=start_time + timedelta(hours=4),
        reporter_id=102,
    )

    attach_report_to_incident(report, incident)
    attach_report_to_incident(report, incident)

    assert incident.report_ids == [1, 2]

def test_process_report_creates_new_incident():
    report = Report(
        id=1,
        description="Projector is broken",
        category="IT",
        subcategory="PROJECTOR",
        location="Room 203",
        reported_at=datetime(2026, 8, 31, 10, 0),
        reporter_id=101,
    )

    incidents = []

    incident, created = process_report(
        report,
        incidents,
        new_incident_id=101,
    )

    assert created is True
    assert incident.id == 101
    assert incident.report_ids == [1]
    assert incident.status == "REPORTED"
    assert len(incidents) == 1

def test_process_report_attaches_to_existing_incident():
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

    incidents = [incident]

    result, created = process_report(
        report,
        incidents,
        new_incident_id=102,
    )

    assert created is False
    assert result is incident
    assert incident.report_ids == [1, 2]
    assert len(incidents) == 1

def test_multiple_reports_over_several_hours_create_one_occurrence():
    reports = [
        Report(
            id=1,
            description="Projector is broken",
            category="IT",
            subcategory="PROJECTOR",
            location="Room 203",
            reported_at=datetime(2026, 8, 31, 10, 0),
            reporter_id=101,
        ),
        Report(
            id=2,
            description="Projector still not working",
            category="IT",
            subcategory="PROJECTOR",
            location="Room 203",
            reported_at=datetime(2026, 8, 31, 11, 30),
            reporter_id=102,
        ),
        Report(
            id=3,
            description="Room 203 projector is not working",
            category="IT",
            subcategory="PROJECTOR",
            location="Room 203",
            reported_at=datetime(2026, 8, 31, 14, 0),
            reporter_id=103,
        ),
        Report(
            id=4,
            description="Projector problem continues",
            category="IT",
            subcategory="PROJECTOR",
            location="Room 203",
            reported_at=datetime(2026, 8, 31, 16, 0),
            reporter_id=104,
        ),
    ]

    incidents = []

    for index, report in enumerate(reports, start=101):
        process_report(
            report,
            incidents,
            new_incident_id=index,
        )

    assert len(incidents) == 1
    assert incidents[0].report_ids == [1, 2, 3, 4]