from copy import deepcopy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Ensure activities are restored between tests"""
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


@pytest.fixture()
def client():
    return TestClient(app)


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_creates_participant(client):
    email = "test_student@mergington.edu"
    activity = "Chess Club"

    # Ensure not registered
    assert email not in activities[activity]["participants"]

    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")

    assert email in activities[activity]["participants"]


def test_signup_duplicate_returns_400(client):
    activity = "Programming Class"
    existing = activities[activity]["participants"][0]

    resp = client.post(f"/activities/{activity}/signup?email={existing}")
    assert resp.status_code == 400


def test_unregister_participant(client):
    activity = "Drama Club"
    email = activities[activity]["participants"][0]

    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    data = resp.json()
    assert "Unregistered" in data.get("message", "")
    assert email not in activities[activity]["participants"]


def test_unregister_missing_returns_404(client):
    activity = "Gym Class"
    email = "not_registered@mergington.edu"

    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 404
