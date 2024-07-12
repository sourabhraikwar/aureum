import pytest
from fastapi.testclient import TestClient
from main import app  # Ensure you import your FastAPI app instance
from fastapi import status

client = TestClient(app)

# Fixtures
@pytest.fixture
def user_data():
    return {
        "username": "testuser",
        "password": "testpassword",
        "email": "testuser@example.com"
    }

@pytest.fixture
def token_headers(user_data):
    response = client.post("/token", data=user_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# Test Cases
def test_create_user(user_data):
    response = client.post("/users/", json=user_data)
    assert response.status_code == status.HTTP_200_OK
    assert "username" in response.json()
    assert response.json()["username"] == user_data["username"]

def test_login_for_access_token(user_data):
    client.post("/users/", json=user_data)  # Ensure user is created first
    response = client.post("/token", data=user_data)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_read_users_me(token_headers):
    response = client.get("/users/me", headers=token_headers)
    assert response.status_code == status.HTTP_200_OK
    assert "username" in response.json()

def test_update_user_partial(token_headers):
    update_data = {"email": "newemail@example.com"}
    response = client.patch("/users/me", json=update_data, headers=token_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == update_data["email"]

def test_update_user_full(user_data, token_headers):
    update_data = {
        "username": user_data["username"],
        "email": "newemail@example.com",
        "password": "newpassword"
    }
    response = client.put("/users/me", json=update_data, headers=token_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == update_data["email"]

def test_delete_user(token_headers):
    response = client.delete("/users/me", headers=token_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Ensure user is actually deleted
    response = client.get("/users/me", headers=token_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
