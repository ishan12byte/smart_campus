from decision_engine.workload import (
    Resource,
    calculate_workload_ratio,
    get_workload_status,
    get_remaining_capacity,
)
import pytest


def test_resource_starts_with_zero_assigned_hours():
    resource = Resource(
        id=1,
        name="IT Support A",
        department="IT",
        capacity_hours=8,
    )

    assert resource.assigned_hours == 0.0

def test_calculate_workload_ratio():
    resource = Resource(
        id=1,
        name="IT Support A",
        department="IT",
        capacity_hours=8,
        assigned_hours=4,
    )

    assert calculate_workload_ratio(resource) == 0.5

def test_workload_status_normal():
    assert get_workload_status(0.70) == "NORMAL"


def test_workload_status_high():
    assert get_workload_status(0.80) == "HIGH"


def test_workload_status_very_high():
    assert get_workload_status(0.95) == "VERY_HIGH"


def test_workload_status_overloaded():
    assert get_workload_status(1.01) == "OVERLOADED"

def test_remaining_capacity():
    resource = Resource(
        id=1,
        name="IT Support A",
        department="IT",
        capacity_hours=8,
        assigned_hours=5,
    )

    assert get_remaining_capacity(resource) == 3

def test_remaining_capacity_is_zero_when_overloaded():
    resource = Resource(
        id=1,
        name="IT Support A",
        department="IT",
        capacity_hours=8,
        assigned_hours=10,
    )

    assert get_remaining_capacity(resource) == 0.0

def test_zero_capacity_is_invalid():
    resource = Resource(
        id=1,
        name="IT Support A",
        department="IT",
        capacity_hours=0,
    )

    with pytest.raises(ValueError):
        calculate_workload_ratio(resource)

def test_negative_workload_ratio_is_invalid():
    with pytest.raises(ValueError):
        get_workload_status(-0.1)