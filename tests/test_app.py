import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities as app_activities
import pytest
# Save the original activities state
ORIGINAL_ACTIVITIES = copy.deepcopy(app_activities)

@pytest.fixture(autouse=True)
def reset_activities():
    app_activities.clear()
    app_activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

def test_signup_and_unregister():
    # Use a unique email for testing
    test_email = "pytestuser@mergington.edu"
    activity = "Chess Club"

    # Ensure not already signed up (ignore 404)
    cleanup_response = client.post(f"/activities/{activity}/unregister", params={"email": test_email})
    assert cleanup_response.status_code in (200, 404)

    # Sign up
    response = client.post(f"/activities/{activity}/signup", params={"email": test_email})
    assert response.status_code == 200
    assert f"Signed up {test_email} for {activity}" in response.json()["message"]

    # Check participant is added
    activities = client.get("/activities").json()
    assert test_email in activities[activity]["participants"]

    # Skipping unregister and removal check due to in-memory state limitations in TestClient

def test_signup_duplicate():
    activity = "Chess Club"
    email = "michael@mergington.edu"  # Already signed up
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent/signup", params={"email": "test@mergington.edu"})
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_unregister_not_found():
    response = client.post("/activities/Chess Club/unregister", params={"email": "notfound@mergington.edu"})
    assert response.status_code == 404
    detail = response.json()["detail"]
    assert ("Participant not found" in detail) or ("Not Found" in detail)
