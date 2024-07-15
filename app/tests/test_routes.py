import pytest
from fastapi import status
from httpx import AsyncClient
import asyncio
from app.main import app
from app.utils import (
    create_access_token,
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_user():
    return {
        "username": "newuser",
        "password": "newpassword",
        "email": "newuser@example.com",
        "full_name": "newuser",
    }


@pytest.fixture
def token(test_user):
    return create_access_token(data={"sub": test_user["username"]})


# Existing test cases...


@pytest.mark.asyncio
async def test_create_user(client):
    new_user = {
        "username": "newuser",
        "full_name": "newuser",
        "password": "newpassword",
        "email": "newuser@example.com",
    }
    response = await client.post("/users/", json=new_user)
    assert response.status_code == status.HTTP_200_OK
    created_user = response.json()
    assert created_user["username"] == new_user["username"]
    assert created_user["email"] == new_user["email"]
    assert "password" not in created_user


@pytest.mark.asyncio
async def test_login_for_access_token_success(client, test_user):
    response = await client.post(
        "/token",
        data={"username": test_user["username"], "password": test_user["password"]},
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_update_user_partial(client, token):
    update_data = {"email": "updated@example.com"}
    response = await client.patch(
        "/users/me", json=update_data, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    updated_user = response.json()
    assert updated_user["email"] == update_data["email"]


@pytest.mark.asyncio
async def test_update_user_full(client, token, test_user):
    update_data = {
        "username": test_user["username"],
        "email": "fullyupdated@example.com",
        "full_name": test_user["full_name"],
        "password": test_user["password"]
    }
    response = await client.put(
        "/users/me", json=update_data, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    updated_user = response.json()
    assert updated_user["email"] == update_data["email"]
    assert "password" not in updated_user


@pytest.mark.asyncio
async def test_delete_user(client, token):
    response = await client.delete(
        "/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_update_user_partial_no_data(client, token):
    response = await client.patch(
        "/users/me", json={}, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "No update data provided"


@pytest.mark.asyncio
async def test_update_nonexistent_user(client):
    # Assuming a token for a non-existent user
    fake_token = create_access_token(data={"sub": "nonexistentuser"})
    update_data = {"email": "fake@example.com"}
    response = await client.patch(
        "/users/me", json=update_data, headers={"Authorization": f"Bearer {fake_token}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Could not validate credentials"


@pytest.mark.asyncio
async def test_delete_nonexistent_user(client):
    # Assuming a token for a non-existent user
    fake_token = create_access_token(data={"sub": "nonexistentuser"})
    response = await client.delete(
        "/users/me", headers={"Authorization": f"Bearer {fake_token}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Could not validate credentials"
