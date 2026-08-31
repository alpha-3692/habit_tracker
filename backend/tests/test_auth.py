import pytest
import time
from datetime import timedelta
from jose import jwt
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token


def test_successful_registration(client):
    payload = {
        "email": "test@example.com",
        "password": "Password123!",
        "full_name": "Test User",
        "timezone": "Asia/Kolkata",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["full_name"] == "Test User"
    assert data["user"]["subscription_tier"] == "free"
    assert "hashed_password" not in data["user"]


def test_duplicate_email_registration(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "Password123!",
        "full_name": "Original User",
    }
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 409
    data = res2.json()
    assert "An account with this email already exists" in data["detail"]


def test_successful_login(client):
    register_payload = {
        "email": "login@example.com",
        "password": "CorrectPassword123!",
        "full_name": "Login User",
    }
    client.post("/api/v1/auth/register", json=register_payload)

    login_payload = {
        "email": "login@example.com",
        "password": "CorrectPassword123!",
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "login@example.com"


def test_incorrect_password(client):
    register_payload = {
        "email": "wrongpw@example.com",
        "password": "RightPassword123!",
    }
    client.post("/api/v1/auth/register", json=register_payload)

    login_payload = {
        "email": "wrongpw@example.com",
        "password": "WrongPassword123!",
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_unknown_email(client):
    login_payload = {
        "email": "unknown@example.com",
        "password": "Password123!",
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_access_token_validation(client):
    register_payload = {
        "email": "authtoken@example.com",
        "password": "Password123!",
    }
    reg_res = client.post("/api/v1/auth/register", json=register_payload)
    token = reg_res.json()["access_token"]

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "authtoken@example.com"


def test_refresh_token_validation(client):
    register_payload = {
        "email": "refreshtoken@example.com",
        "password": "Password123!",
    }
    reg_res = client.post("/api/v1/auth/register", json=register_payload)
    refresh_token = reg_res.json()["refresh_token"]

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_expired_token(client):
    # Manually generate an expired access token
    expired_payload = {
        "sub": "00000000-0000-0000-0000-000000000000",
        "iat": time.time() - 3600,
        "exp": time.time() - 1800,  # Expired 30 mins ago
        "type": "access",
    }
    expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401


def test_invalid_token(client):
    invalid_token = "not.a.valid.jwt.token"
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    assert response.status_code == 401
