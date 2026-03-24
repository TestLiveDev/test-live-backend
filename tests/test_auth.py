import pytest


@pytest.mark.asyncio
async def test_register_and_login(raw_client):
    register_response = await raw_client.post(
        "/api/auth/register",
        json={
            "email": "user@example.com",
            "password": "password123",
            "full_name": "Test User",
        },
    )

    assert register_response.status_code == 201

    login_response = await raw_client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "password123"},
    )

    assert login_response.status_code == 200
    data = login_response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_me_returns_current_user(raw_client):
    await raw_client.post(
        "/api/auth/register",
        json={"email": "user@example.com", "password": "password123"},
    )
    login_response = await raw_client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    response = await raw_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"
