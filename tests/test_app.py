from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that root path redirects to static/index.html"""
    response = client.get("/")
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data

def test_signup_success():
    """Test successful activity signup"""
    activity = "Chess Club"
    email = "new.student@mergington.edu"
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Signed up {email} for {activity}"

    # Verify student was added
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]

def test_signup_duplicate():
    """Test signup with already registered email"""
    activity = "Programming Class"
    email = "emma@mergington.edu"  # Already registered in this activity
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"].lower()

def test_signup_nonexistent_activity():
    """Test signup for non-existent activity"""
    activity = "Nonexistent Club"
    email = "test@mergington.edu"
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()

def test_unregister_success():
    """Test successful activity unregistration"""
    activity = "Chess Club"
    email = "daniel@mergington.edu"  # Using an email we know is registered
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Unregistered {email} from {activity}"

    # Verify student was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]

def test_unregister_not_registered():
    """Test unregistering a student who isn't registered"""
    activity = "Chess Club"
    email = "not.registered@mergington.edu"
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 400
    data = response.json()
    assert "not registered" in data["detail"].lower()

def test_unregister_nonexistent_activity():
    """Test unregistering from non-existent activity"""
    activity = "Nonexistent Club"
    email = "test@mergington.edu"
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()