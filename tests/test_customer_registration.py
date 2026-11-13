import json
import pytest

from fastapi.testclient import TestClient
from argon2 import PasswordHasher

from app.repositories.user_repository import UserRepository

def test_registration_page(registration_client):
    client, _ = registration_client

    response = client.get("/frontend/register.html")

    assert response.status_code == 200
    assert 'id="register-form"' in response.text
    assert 'src="/frontend/register.js"' in response.text


def test_registration_javascript(registration_client):
    client, _ = registration_client

    response = client.get("/frontend/register.js")

    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]

@pytest.fixture
def registration_client(tmp_path, monkeypatch):
    users_path = tmp_path / "users.json"
    users_path.write_text("[]", encoding="utf-8")

    monkeypatch.setenv("USERS_DATA_PATH", str(users_path))

    from app.main import app

    with TestClient(app) as client:
        yield client, users_path

@pytest.fixture
def valid_customer():
    return {
        "name": "Alex Customer",
        "email": "alex@example.com",
        "password": "secure-password-123",
        "delivery_address": "123 Test Street"
    }

def test_register_customer(registration_client, valid_customer):
    client, users_path = registration_client

    response = client.post("/customers", json=valid_customer)

    assert response.status_code == 201

    result = response.json()

    assert result["id"] == 1
    assert result["role"] == "customer"
    assert result["is_active"] is True
    assert result["email"] == "alex@example.com"
    assert result["delivery_address"] == "123 Test Street"

    assert "password" not in result
    assert "password_hash" not in result

    saved = json.loads(
        users_path.read_text(encoding="utf-8")
    )

    assert len(saved) == 1
    assert saved[0]["password_hash"] != valid_customer["password"]

    assert PasswordHasher().verify(
        saved[0]["password_hash"],
        valid_customer["password"]
    )

def test_duplicate_email(registration_client, valid_customer):
    client, users_path = registration_client

    assert client.post(
        "/customers", json=valid_customer
    ).status_code == 201

    second = {**valid_customer, "email": "ALEX@example.com"}

    assert client.post(
        "/customers", json=second
    ).status_code == 409

    saved = json.loads(
        users_path.read_text(encoding="utf-8")
    )
    assert len(saved) == 1

@pytest.mark.parametrize("changes", [
    {"email": "not-an-email"},
    {"password": "short"},
    {"name": "   "},
])
def test_invalid_registration(
    registration_client, valid_customer, changes
):
    client, users_path = registration_client

    response = client.post(
        "/customers",
        json={**valid_customer, **changes}
    )

    assert response.status_code == 422

    saved = json.loads(
        users_path.read_text(encoding="utf-8")
    )
    assert saved == []

def test_user_id_remains_stable(
    registration_client, valid_customer
):
    client, users_path = registration_client

    response = client.post("/customers", json=valid_customer)
    assert response.status_code == 201

    second = {
        **valid_customer,
        "email": "second@example.com"
    }

    response = client.post("/customers", json=second)
    assert response.status_code == 201
    assert response.json()["id"] == 2

    users = UserRepository(users_path).get_all()

    assert [user.id for user in users] == [1, 2]
    assert users[0].email == valid_customer["email"]

def test_customer_cannot_choose_role(
    registration_client, valid_customer
):
    client, users_path = registration_client

    customer = {
        **valid_customer,
        "role": "admin"
    }

    response = client.post("/customers", json=customer)

    assert response.status_code == 201
    assert response.json()["role"] == "customer"

    saved = json.loads(
        users_path.read_text(encoding="utf-8")
    )

    assert saved[0]["role"] == "customer"
