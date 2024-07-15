import pytest
from fastapi.testclient import TestClient
from app.main import app
from fastapi import status
from httpx import AsyncClient

client = TestClient(app)


# Fixtures
@pytest.fixture
def user_data():
    """fixture provides test user data
    """
    return {
        "username": "testuser",
        "full_name": "testuser",
        "password": "testpassword",
        "email": "testuser@example.com"
    }


@pytest.fixture
def token_headers(user_data):
    """
    fixture for creating token header
    """
    response = client.post("/token", data=user_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_user(user_data):
    """
    Tests create user API
    """
    response = client.post("/users/", json=user_data)
    assert response.status_code == status.HTTP_200_OK
    assert "username" in response.json()
    assert response.json()["username"] == user_data["username"]