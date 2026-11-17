import json
import pytest
import jwt
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone


@pytest.fixture
def auth_client(tmp_path, monkeypatch):
    users_path = tmp_path / "users.json"
    users_path.write_text("[]", encoding="utf-8")

    monkeypatch.setenv("USERS_DATA_PATH", str(users_path))
    monkeypatch.setenv(
        "AUTH_SECRET_KEY",
        "test-only-secret-1234567890-abcdefghijklmnopqrstuvwxyz"
    )

    from app.main import app

    with TestClient(app) as client:
        yield client, users_path

def register_customer(client):
    customer = {
        "name": "Alex Customer",
        "email": "alex@example.com",
        "password": "secure-password-123"
    }

    response = client.post("/customers", json=customer)

    assert response.status_code == 201

    return customer

def test_successful_login(auth_client):
    client, _ = auth_client

    customer = register_customer(client)

    response = client.post("/auth/login", json={
        "email": customer["email"],
        "password": customer["password"]
    })

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"

    token = response.json()["access_token"]
    assert token

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["role"] == "customer"
    assert response.json()["email"] == customer["email"]
    assert "password_hash" not in response.json()

def test_wrong_password(auth_client):
    client, _ = auth_client

    register_customer(client)

    response = client.post("/auth/login", json={
        "email": "alex@example.com",
        "password": "wrong-password"
    })

    assert response.status_code == 401


def test_unknown_email(auth_client):
    client, _ = auth_client

    response = client.post("/auth/login", json={
        "email": "unknown@example.com",
        "password": "some-password"
    })

    assert response.status_code == 401

def test_missing_authentication(auth_client):
    client, _ = auth_client

    response = client.get("/auth/me")

    assert response.status_code == 401


def test_invalid_token(auth_client):
    client, _ = auth_client

    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401

def test_deactivated_user_cannot_login(auth_client):
    client, users_path = auth_client

    register_customer(client)

    users = json.loads(
        users_path.read_text(encoding="utf-8")
    )

    users[0]["is_active"] = False

    users_path.write_text(
        json.dumps(users),
        encoding="utf-8"
    )

    response = client.post("/auth/login", json={
        "email": "alex@example.com",
        "password": "secure-password-123"
    })

    assert response.status_code == 401

def test_deactivated_user_cannot_use_token(auth_client):
    client, users_path = auth_client

    customer = register_customer(client)

    login_response = client.post("/auth/login", json={
        "email": customer["email"],
        "password": customer["password"]
    })

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    users = json.loads(
        users_path.read_text(encoding="utf-8")
    )

    users[0]["is_active"] = False

    users_path.write_text(
        json.dumps(users),
        encoding="utf-8"
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    
def test_expired_token(auth_client):
    client, _ = auth_client

    register_customer(client)

    expired_token = jwt.encode(
        {
            "sub": "1",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1)
        },
        "test-only-secret-1234567890-abcdefghijklmnopqrstuvwxyz",
        algorithm="HS256"
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )

    assert response.status_code == 401
