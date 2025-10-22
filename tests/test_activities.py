import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that root endpoint redirects to static/index.html"""
    response = client.get("/")
    assert response.status_code == 200  # FastAPI StaticFiles returns 200
    assert "text/html" in response.headers["content-type"]

def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    # Test structure of an activity
    activity = list(activities.values())[0]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity

def test_signup_flow():
    """Test the complete signup flow for an activity"""
    # Get available activities
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]
    
    # Try to sign up a new participant
    test_email = "test.student@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify participant was added
    response = client.get("/activities")
    activities = response.json()
    assert test_email in activities[activity_name]["participants"]
    
    # Try to sign up the same participant again (should fail)
    response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_unregister_flow():
    """Test the complete unregister flow for an activity"""
    # Get available activities
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]
    
    # First sign up a test participant
    test_email = "unregister.test@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    assert response.status_code == 200
    
    # Now unregister the participant
    response = client.post(f"/activities/{activity_name}/unregister?email={test_email}")
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert test_email not in activities[activity_name]["participants"]
    
    # Try to unregister the same participant again (should fail)
    response = client.post(f"/activities/{activity_name}/unregister?email={test_email}")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]

def test_nonexistent_activity():
    """Test handling of requests for non-existent activities"""
    fake_activity = "FakeActivity123"
    test_email = "test@mergington.edu"
    
    # Try to sign up for non-existent activity
    response = client.post(f"/activities/{fake_activity}/signup?email={test_email}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
    
    # Try to unregister from non-existent activity
    response = client.post(f"/activities/{fake_activity}/unregister?email={test_email}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]