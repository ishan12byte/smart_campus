import os
from datetime import datetime, timedelta, timezone

import jwt

from app.models.incident import Incident


def incident_payload(location="Integration Test Room 999"):
    return {
        "title": "Integration Test - Electrical Issue",
        "description": "Testing the Smart Campus API",
        "category": "MAINTENANCE",
        "subcategory": "ELECTRICAL",
        "location": location,
        "impact": 4,
        "urgency": 4,
        "safety": 2,
        "deadline": 3,
        "recurrence": 1,
        "evidence_available": False,
    }


def test_student_login_success(client, test_data):
    response = client.post(
        "/auth/login",
        json={
            "email": "student@test.com",
            "password": "TestPassword@123",
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_invalid_login_rejected(client, test_data):
    response = client.post(
        "/auth/login",
        json={
            "email": "student@test.com",
            "password": "WrongPassword",
        },
    )

    assert response.status_code == 401


def test_authenticated_user_can_access_me(client, auth_headers):
    response = client.get(
        "/auth/me",
        headers=auth_headers("student"),
    )

    assert response.status_code == 200
    assert response.json()["email"] == "student@test.com"


def test_unauthenticated_incident_access_rejected(client):
    response = client.get("/incidents")

    assert response.status_code in (401, 403)


def test_student_can_create_incident(client, auth_headers):
    response = client.post(
        "/incidents",
        headers=auth_headers("student"),
        json=incident_payload(),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["category"] == "MAINTENANCE"
    assert data["responsible_department_id"] is not None
    assert data["priority_score"] is not None
    assert data["priority_level"] in (
        "LOW", "MEDIUM", "HIGH", "CRITICAL"
    )


def test_invalid_subcategory_rejected(client, auth_headers):
    payload = incident_payload()
    payload["subcategory"] = "INVALID_CATEGORY"

    response = client.post(
        "/incidents",
        headers=auth_headers("student"),
        json=payload,
    )

    assert response.status_code == 422


def test_incident_recurrence_and_assignment_preservation(
    client, auth_headers
):
    headers = auth_headers("student")
    payload = incident_payload("Recurrence Test Room")

    first = client.post(
        "/incidents",
        headers=headers,
        json=payload,
    )

    assert first.status_code == 201
    first_data = first.json()

    original_id = first_data["id"]
    original_assignee = first_data["assigned_to_id"]

    second = client.post(
        "/incidents",
        headers=headers,
        json=payload,
    )

    assert second.status_code == 201
    second_data = second.json()

    assert second_data["id"] == original_id
    assert second_data["assigned_to_id"] == original_assignee

    reports = client.get(
        f"/incidents/{original_id}/reports",
        headers=headers,
    )

    assert reports.status_code == 200
    assert len(reports.json()) == 2


def test_student_cannot_acknowledge_own_incident(
    client, auth_headers
):
    student_headers = auth_headers("student")

    created = client.post(
        "/incidents",
        headers=student_headers,
        json=incident_payload("Student Permission Test Room"),
    )

    assert created.status_code == 201
    incident_id = created.json()["id"]

    response = client.post(
        f"/incidents/{incident_id}/action/acknowledge",
        headers=student_headers,
        json={"note": "Student cannot acknowledge"},
    )

    assert response.status_code == 403


def test_staff_can_process_assigned_incident(
    client, auth_headers
):
    student_headers = auth_headers("student")
    staff_headers = auth_headers("staff")

    created = client.post(
        "/incidents",
        headers=student_headers,
        json=incident_payload("Lifecycle Test Room"),
    )

    assert created.status_code == 201
    incident = created.json()
    incident_id = incident["id"]

    if incident["assigned_to_id"] != None:
        assert incident["assigned_to_id"] == 2

    acknowledge = client.post(
        f"/incidents/{incident_id}/action/acknowledge",
        headers=staff_headers,
        json={"note": "Acknowledged by staff"},
    )

    assert acknowledge.status_code == 200
    assert acknowledge.json()["status"] == "ACKNOWLEDGED"

    start = client.post(
        f"/incidents/{incident_id}/action/start",
        headers=staff_headers,
        json={"note": "Work started"},
    )

    assert start.status_code == 200
    assert start.json()["status"] == "IN_PROGRESS"

    resolve = client.post(
        f"/incidents/{incident_id}/action/resolve",
        headers=staff_headers,
        json={"note": "Issue resolved"},
    )

    assert resolve.status_code == 200
    assert resolve.json()["status"] == "RESOLVED"

    verify = client.post(
        f"/incidents/{incident_id}/action/verify",
        headers=student_headers,
        json={"note": "Resolution verified"},
    )

    assert verify.status_code == 200
    assert verify.json()["status"] == "VERIFIED"

    history = client.get(
        f"/incidents/{incident_id}/history",
        headers=student_headers,
    )

    assert history.status_code == 200

    actions = [item["action"] for item in history.json()]

    assert actions == [
        "ACKNOWLEDGE",
        "START",
        "RESOLVE",
        "VERIFY",
    ]


def test_student_cannot_view_another_students_incident(
    client, auth_headers
):
    first_headers = auth_headers("student")
    second_headers = auth_headers("other_student")

    created = client.post(
        "/incidents",
        headers=first_headers,
        json=incident_payload("Private Incident Room"),
    )

    assert created.status_code == 201
    incident_id = created.json()["id"]

    response = client.get(
        f"/incidents/{incident_id}",
        headers=second_headers,
    )

    assert response.status_code == 404


def test_super_admin_can_list_users(client, auth_headers):
    response = client.get(
        "/users/",
        headers=auth_headers("admin"),
    )

    assert response.status_code == 200
    assert len(response.json()) == 5


def test_student_cannot_list_users(client, auth_headers):
    response = client.get(
        "/users/",
        headers=auth_headers("student"),
    )

    assert response.status_code == 403


def test_department_list_requires_authentication(client):
    response = client.get("/departments")

    assert response.status_code in (401, 403)


def test_student_cannot_access_admin_test(client, auth_headers):
    response = client.get(
        "/admin/test",
        headers=auth_headers("student"),
    )

    assert response.status_code == 403


def test_super_admin_can_access_admin_test(client, auth_headers):
    response = client.get(
        "/admin/test",
        headers=auth_headers("admin"),
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Admin access granted"


def test_student_cannot_create_department(client, auth_headers):
    response = client.post(
        "/departments",
        headers=auth_headers("student"),
        json={
            "code": "NEW_DEPT",
            "name": "New Department",
            "description": "Test department"
        }
    )
    assert response.status_code == 403


def test_staff_cannot_create_department(client, auth_headers):
    response = client.post(
        "/departments",
        headers=auth_headers("staff"),
        json={
            "code": "NEW_DEPT",
            "name": "New Department",
            "description": "Test department"
        }
    )
    assert response.status_code == 403


def test_student_cannot_update_department(client, auth_headers):
    response = client.put(
        "/departments/1",
        headers=auth_headers("student"),
        json={"name": "Updated Department"}
    )
    assert response.status_code == 403


def test_super_admin_can_create_department(client, auth_headers):
    response = client.post(
        "/departments",
        headers=auth_headers("admin"),
        json={
            "code": "NEW_DEPT",
            "name": "New Department",
            "description": "Created by super admin"
        }
    )
    assert response.status_code == 201
    assert response.json()["code"] == "NEW_DEPT"


def test_super_admin_can_update_department(client, auth_headers):
    response = client.put(
        "/departments/1",
        headers=auth_headers("admin"),
        json={"name": "Updated Maintenance"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Maintenance"


def test_tampered_token_is_rejected(client, auth_headers):
    headers = auth_headers("student")
    token = headers["Authorization"].replace("Bearer ", "")

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}tampered"}
    )

    assert response.status_code == 401

def test_expired_token_is_rejected(client, test_data):
    user = test_data["users"]["student"]

    expired_token = jwt.encode(
        {
            "sub": str(user.id),
            "exp": datetime.now(timezone.utc) - timedelta(minutes=5)
        },
        os.getenv("JWT_SECRET_KEY"),
        algorithm="HS256"
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )

    assert response.status_code == 401


def test_wrong_secret_token_is_rejected(client, test_data):
    user = test_data["users"]["student"]

    wrong_token = jwt.encode(
        {
            "sub": str(user.id),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
        },
        "completely-wrong-secret-key-for-testing-123456",
        algorithm="HS256"
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {wrong_token}"}
    )

    assert response.status_code == 401


def test_inactive_user_cannot_access_api(
    client, auth_headers, test_data, db_session
):
    headers = auth_headers("student")

    user = test_data["users"]["student"]
    user.is_active = False
    db_session.commit()

    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 403

def test_registration_assigns_student_role(client, test_data):
    response = client.post(
        "/auth/register",
        json={
            "name": "New Student",
            "email": "newstudent@test.com",
            "password": "NewPassword@123",
            "department_id": test_data["departments"]["IT"].id,
            "role_id": test_data["roles"]["SUPER_ADMIN"].id
        }
    )

    assert response.status_code == 201
    assert response.json()["role_id"] == test_data["roles"]["STUDENT"].id
    assert "password_hash" not in response.json()


def test_registration_rejects_duplicate_email(client, test_data):
    response = client.post(
        "/auth/register",
        json={
            "name": "Duplicate Student",
            "email": "student@test.com",
            "password": "NewPassword@123",
            "department_id": test_data["departments"]["IT"].id
        }
    )

    assert response.status_code == 400


def test_registration_rejects_invalid_department(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "New Student",
            "email": "invaliddept@test.com",
            "password": "NewPassword@123",
            "department_id": 9999
        }
    )

    assert response.status_code == 400


def test_registration_rejects_inactive_department(
    client, db_session, test_data
):
    department = test_data["departments"]["IT"]
    department.is_active = False
    db_session.commit()

    response = client.post(
        "/auth/register",
        json={
            "name": "New Student",
            "email": "inactive@test.com",
            "password": "NewPassword@123",
            "department_id": department.id
        }
    )

    assert response.status_code == 400

def test_staff_cannot_view_unassigned_other_department_incident(
    client, auth_headers, test_data, db_session
):
    created = client.post(
        "/incidents",
        headers=auth_headers("student"),
        json=incident_payload("Cross Department Test Room")
    )

    assert created.status_code == 201
    incident_id = created.json()["id"]

    # Move staff to IT and remove the assignment.
    staff = test_data["users"]["staff"]
    staff.department_id = test_data["departments"]["IT"].id

    incident = db_session.query(Incident).filter(
        Incident.id == incident_id
    ).first()
    incident.assigned_to_id = None
    db_session.commit()

    response = client.get(
        f"/incidents/{incident_id}",
        headers=auth_headers("staff")
    )

    assert response.status_code == 404


def test_assigned_staff_can_view_incident_even_if_department_differs(
    client, auth_headers, test_data, db_session
):
    created = client.post(
        "/incidents",
        headers=auth_headers("student"),
        json=incident_payload("Assigned Cross Department Room")
    )

    assert created.status_code == 201
    incident_id = created.json()["id"]

    staff = test_data["users"]["staff"]
    staff.department_id = test_data["departments"]["IT"].id
    db_session.commit()

    response = client.get(
        f"/incidents/{incident_id}",
        headers=auth_headers("staff")
    )

    assert response.status_code == 200


def test_department_head_cannot_view_other_department_incident(
    client, auth_headers, test_data, db_session
):
    created = client.post(
        "/incidents",
        headers=auth_headers("student"),
        json=incident_payload("Head Access Test Room")
    )

    assert created.status_code == 201
    incident_id = created.json()["id"]

    head = test_data["users"]["head"]
    head.department_id = test_data["departments"]["IT"].id
    db_session.commit()

    response = client.get(
        f"/incidents/{incident_id}",
        headers=auth_headers("head")
    )

    assert response.status_code == 404


def test_department_head_can_view_own_department_incident(
    client, auth_headers
):
    created = client.post(
        "/incidents",
        headers=auth_headers("student"),
        json=incident_payload("Department Head Own Department Room")
    )

    assert created.status_code == 201

    response = client.get(
        f"/incidents/{created.json()['id']}",
        headers=auth_headers("head")
    )

    assert response.status_code == 200


def test_super_admin_can_view_any_department_incident(
    client, auth_headers
):
    created = client.post(
        "/incidents",
        headers=auth_headers("student"),
        json=incident_payload("Super Admin Visibility Room")
    )

    assert created.status_code == 201

    response = client.get(
        f"/incidents/{created.json()['id']}",
        headers=auth_headers("admin")
    )

    assert response.status_code == 200

def test_assigned_staff_can_process_incident_from_other_department(
    client, auth_headers, test_data, db_session
):
    created = client.post(
        "/incidents",
        headers=auth_headers("student"),
        json=incident_payload("Cross Department Action Room")
    )

    assert created.status_code == 201
    incident_id = created.json()["id"]

    # Move the assigned staff member to another department.
    staff = test_data["users"]["staff"]
    staff.department_id = test_data["departments"]["IT"].id
    db_session.commit()

    # Assigned staff should still be able to acknowledge.
    response = client.post(
        f"/incidents/{incident_id}/action/acknowledge",
        headers=auth_headers("staff"),
        json={"note": "Cross-department acknowledgement"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ACKNOWLEDGED"


def test_unassigned_other_department_staff_cannot_acknowledge(
    client, auth_headers, test_data, db_session
):
    created = client.post(
        "/incidents",
        headers=auth_headers("student"),
        json=incident_payload("Unassigned Cross Department Room")
    )

    assert created.status_code == 201
    incident_id = created.json()["id"]

    staff = test_data["users"]["staff"]
    staff.department_id = test_data["departments"]["IT"].id

    incident = db_session.query(Incident).filter(
        Incident.id == incident_id
    ).first()
    incident.assigned_to_id = None
    db_session.commit()

    response = client.post(
        f"/incidents/{incident_id}/action/acknowledge",
        headers=auth_headers("staff"),
        json={"note": "Unauthorized acknowledgement"}
    )

    assert response.status_code == 404


def test_department_head_cannot_process_other_department_incident(
    client, auth_headers, test_data, db_session
):
    created = client.post(
        "/incidents",
        headers=auth_headers("student"),
        json=incident_payload("Head Cross Department Action Room")
    )

    assert created.status_code == 201
    incident_id = created.json()["id"]

    head = test_data["users"]["head"]
    head.department_id = test_data["departments"]["IT"].id
    db_session.commit()

    response = client.post(
        f"/incidents/{incident_id}/action/acknowledge",
        headers=auth_headers("head"),
        json={"note": "Unauthorized head acknowledgement"}
    )

    assert response.status_code == 404

def test_staff_cannot_verify_resolved_incident(
    client, auth_headers
):
    student_headers = auth_headers("student")
    staff_headers = auth_headers("staff")

    created = client.post(
        "/incidents",
        headers=student_headers,
        json=incident_payload("Staff Verification Permission Room")
    )

    assert created.status_code == 201
    incident_id = created.json()["id"]

    # Staff acknowledges the incident.
    acknowledge = client.post(
        f"/incidents/{incident_id}/action/acknowledge",
        headers=staff_headers,
        json={"note": "Acknowledged"}
    )
    assert acknowledge.status_code == 200

    # Staff starts the work.
    start = client.post(
        f"/incidents/{incident_id}/action/start",
        headers=staff_headers,
        json={"note": "Work started"}
    )
    assert start.status_code == 200

    # Staff resolves the incident.
    resolve = client.post(
        f"/incidents/{incident_id}/action/resolve",
        headers=staff_headers,
        json={"note": "Work completed"}
    )
    assert resolve.status_code == 200

    # Staff must not verify their own resolution.
    verify = client.post(
        f"/incidents/{incident_id}/action/verify",
        headers=staff_headers,
        json={"note": "Unauthorized verification"}
    )

    assert verify.status_code == 403

def test_student_cannot_start_or_resolve_own_incident(
    client, auth_headers
):
    headers = auth_headers("student")

    created = client.post(
        "/incidents",
        headers=headers,
        json=incident_payload("Student Lifecycle Security Room")
    )
    assert created.status_code == 201

    incident_id = created.json()["id"]

    start = client.post(
        f"/incidents/{incident_id}/action/start",
        headers=headers,
        json={"note": "Student attempting to start"}
    )
    assert start.status_code == 403

    resolve = client.post(
        f"/incidents/{incident_id}/action/resolve",
        headers=headers,
        json={"note": "Student attempting to resolve"}
    )
    assert resolve.status_code == 403


def test_staff_cannot_reopen_verified_incident(
    client, auth_headers
):
    student_headers = auth_headers("student")
    staff_headers = auth_headers("staff")

    created = client.post(
        "/incidents",
        headers=student_headers,
        json=incident_payload("Staff Reopen Permission Room")
    )
    assert created.status_code == 201

    incident_id = created.json()["id"]

    for action in ["acknowledge", "start", "resolve"]:
        response = client.post(
            f"/incidents/{incident_id}/action/{action}",
            headers=staff_headers,
            json={"note": f"Testing {action}"}
        )
        assert response.status_code == 200

    verify = client.post(
        f"/incidents/{incident_id}/action/verify",
        headers=student_headers,
        json={"note": "Verified by reporter"}
    )
    assert verify.status_code == 200

    reopen = client.post(
        f"/incidents/{incident_id}/action/reopen",
        headers=staff_headers,
        json={"note": "Unauthorized reopen"}
    )
    assert reopen.status_code == 403