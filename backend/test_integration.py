from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.seed import seed_data

client = TestClient(app)

def test_full_pipeline():
    seed_data()

    # 1. Login as student
    login_resp = client.post(
        "/auth/login",
        json={"email": "student@campus.edu", "password": "password123"}
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {token}"}

    # 2. Student reports an electrical incident
    incident_payload = {
        "title": "Sparking outlet in Lab 204",
        "description": "Electrical sparks coming from power outlet near workbench",
        "category": "MAINTENANCE",
        "subcategory": "ELECTRICAL",
        "location": "Engineering Block B, Lab 204",
        "impact": 4,
        "urgency": 4,
        "safety": 5,
        "deadline": 3,
        "recurrence": 1,
    }
    create_resp = client.post("/incidents", json=incident_payload, headers=student_headers)
    assert create_resp.status_code == 201, f"Create incident failed: {create_resp.text}"
    data = create_resp.json()
    inc_id = data["id"]
    print("Created incident data:", data)
    assert data["priority_level"] in ["HIGH", "CRITICAL"]
    assert data["status"] == "REPORTED"

    # 3. Staff login
    staff_login = client.post(
        "/auth/login",
        json={"email": "staff@campus.edu", "password": "password123"}
    )
    assert staff_login.status_code == 200
    staff_token = staff_login.json()["access_token"]
    staff_headers = {"Authorization": f"Bearer {staff_token}"}

    # 4. Staff acknowledges incident
    ack_resp = client.post(f"/incidents/{inc_id}/action/acknowledge", headers=staff_headers)
    assert ack_resp.status_code == 200
    assert ack_resp.json()["status"] == "ACKNOWLEDGED"

    # 5. Staff starts work
    start_resp = client.post(f"/incidents/{inc_id}/action/start", headers=staff_headers)
    assert start_resp.status_code == 200
    assert start_resp.json()["status"] == "IN_PROGRESS"

    # 6. Staff marks resolved
    resolve_resp = client.post(f"/incidents/{inc_id}/action/resolve", headers=staff_headers)
    assert resolve_resp.status_code == 200
    assert resolve_resp.json()["status"] == "VERIFICATION_PENDING"

    # 7. Student verifies resolution
    verify_resp = client.post(f"/incidents/{inc_id}/action/verify", headers=student_headers)
    assert verify_resp.status_code == 200
    assert verify_resp.json()["status"] == "CLOSED"

    # 8. Test Emergency Override
    emergency_payload = {
        "title": "Smoke detector triggered in Library",
        "description": "Flames reported near archives",
        "category": "SECURITY",
        "subcategory": "SAFETY_HAZARD",
        "location": "Central Library, 2nd Floor",
        "impact": 5,
        "urgency": 5,
        "safety": 5,
        "deadline": 5,
        "recurrence": 1,
        "incident_type": "FIRE",
    }
    em_resp = client.post("/incidents", json=emergency_payload, headers=student_headers)
    assert em_resp.status_code == 201
    em_data = em_resp.json()
    assert em_data["priority_level"] == "CRITICAL"
    assert em_data["escalation_level"] == "SUPER_ADMIN"
    print("Emergency override verified successfully:", em_data)

if __name__ == "__main__":
    test_full_pipeline()
    print("ALL BACKEND INTEGRATION TESTS PASSED!")
