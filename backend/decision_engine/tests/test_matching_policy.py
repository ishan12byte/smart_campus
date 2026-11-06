import pytest

from decision_engine.matching_policy import (
    PERSISTENT,
    SERVICE_CYCLE,
    SESSION,
    get_matching_policy,
)


# -------------------------
# Persistent incidents
# -------------------------

def test_projector_is_persistent():
    assert get_matching_policy("PROJECTOR") == PERSISTENT


def test_network_is_persistent():
    assert get_matching_policy("NETWORK") == PERSISTENT


def test_electrical_is_persistent():
    assert get_matching_policy("ELECTRICAL") == PERSISTENT


def test_plumbing_is_persistent():
    assert get_matching_policy("PLUMBING") == PERSISTENT


def test_classroom_equipment_is_persistent():
    assert get_matching_policy("CLASSROOM_EQUIPMENT") == PERSISTENT


def test_security_equipment_is_persistent():
    assert get_matching_policy("SECURITY_EQUIPMENT") == PERSISTENT


# -------------------------
# Service-cycle incidents
# -------------------------

def test_cleaning_is_service_cycle():
    assert get_matching_policy("CLEANING") == SERVICE_CYCLE


def test_waste_is_service_cycle():
    assert get_matching_policy("WASTE") == SERVICE_CYCLE


def test_washroom_is_service_cycle():
    assert get_matching_policy("WASHROOM") == SERVICE_CYCLE


def test_water_sanitation_is_service_cycle():
    assert get_matching_policy("WATER_SANITATION") == SERVICE_CYCLE


# -------------------------
# Session-based incidents
# -------------------------

def test_hall_allocation_is_session():
    assert get_matching_policy("HALL_ALLOCATION") == SESSION


def test_timetable_issue_is_session():
    assert get_matching_policy("TIMETABLE_ISSUE") == SESSION


def test_invigilator_unavailable_is_session():
    assert get_matching_policy("INVIGILATOR_UNAVAILABLE") == SESSION


def test_no_teacher_assigned_is_session():
    assert get_matching_policy("NO_TEACHER_ASSIGNED") == SESSION


def test_no_substitute_is_session():
    assert get_matching_policy("NO_SUBSTITUTE") == SESSION


def test_class_conflict_is_session():
    assert get_matching_policy("CLASS_CONFLICT") == SESSION


# -------------------------
# Input handling
# -------------------------

def test_subcategory_is_case_insensitive():
    assert get_matching_policy("projector") == PERSISTENT


def test_subcategory_with_spaces_is_handled():
    assert get_matching_policy("  PROJECTOR  ") == PERSISTENT


def test_unknown_subcategory_uses_default_policy():
    assert get_matching_policy("UNKNOWN_ISSUE") == PERSISTENT


# -------------------------
# Invalid input
# -------------------------

def test_empty_subcategory_raises_error():
    with pytest.raises(ValueError):
        get_matching_policy("")


def test_whitespace_only_subcategory_raises_error():
    with pytest.raises(ValueError):
        get_matching_policy("   ")