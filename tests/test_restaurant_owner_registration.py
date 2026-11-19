import json
import pytest
from argon2 import PasswordHasher
from fastapi.testclient import TestClient

OWNER = {
    "name": "Alex Owner",
    "email": "alex@example.com",
    "password": "secure-password-123"
}

RESTAURANT = {
    "name": "Test Tacos",
    "cuisine": "Mexican",
    "delivery_time_minutes": 20,
    "delivery_fee": 1.99,
    "address": "3 Test St"
}

MENU_ITEM = {
    "name": "Veggie Tacos",
    "description": "Vegetarian tacos",
    "price": 12.99,
    "is_available": True
}

@pytest.fixture
def owner_client(tmp_path, monkeypatch):
    users_path = tmp_path / "users.json"
    restaurants_path = tmp_path / "restaurants.json"
    menu_path = tmp_path / "menu_items.json"

    users_path.write_text("[]")
    restaurants_path.write_text("[]")
    menu_path.write_text("[]")

    monkeypatch.setenv("USERS_DATA_PATH", str(users_path))
    monkeypatch.setenv("RESTAURANTS_DATA_PATH", str(restaurants_path))
    monkeypatch.setenv("MENU_ITEMS_DATA_PATH", str(menu_path))
    monkeypatch.setenv(
        "AUTH_SECRET_KEY",
        "test-only-secret-for-owner-registration-123456"
    )

    from app.main import app

    with TestClient(app) as client:
        yield client, users_path

def test_owner_registration_page(owner_client):
    client, _ = owner_client

    response = client.get("/frontend/owner-register.html")

    assert response.status_code == 200
    assert 'id="owner-register-form"' in response.text
    assert 'src="/frontend/owner-register.js"' in response.text

    response = client.get("/frontend/register.html")

    assert response.status_code == 200
    assert "/frontend/owner-register.html" in response.text

def test_owner_registration_javascript(owner_client):
    client, _ = owner_client

    response = client.get("/frontend/owner-register.js")

    assert response.status_code == 200
    assert 'fetch("/restaurant-owners"' in response.text

def test_register_restaurant_owner(owner_client):
    client, users_path = owner_client

    response = client.post("/restaurant-owners", json=OWNER)

    assert response.status_code == 201

    result = response.json()

    assert result["id"] == 1
    assert result["role"] == "restaurant owner"
    assert result["is_active"] is True
    assert result["email"] == OWNER["email"]

    assert "password" not in result
    assert "password_hash" not in result
    assert "restaurant_ids" not in result

    users = json.loads(users_path.read_text())

    assert len(users) == 1
    assert users[0]["restaurant_ids"] == []
    assert users[0]["password_hash"] != OWNER["password"]

    assert PasswordHasher().verify(
        users[0]["password_hash"],
        OWNER["password"]
    )

def test_duplicate_owner_email(owner_client):
    client, users_path = owner_client

    assert client.post(
        "/restaurant-owners", json=OWNER
    ).status_code == 201

    duplicate = {**OWNER, "email": "ALEX@example.com"}

    response = client.post("/restaurant-owners", json=duplicate)

    assert response.status_code == 409

    users = json.loads(users_path.read_text())
    assert len(users) == 1

def test_cannot_reuse_customer_email(owner_client):
    client, users_path = owner_client

    response = client.post("/customers", json=OWNER)
    assert response.status_code == 201

    response = client.post("/restaurant-owners", json=OWNER)
    assert response.status_code == 409

    users = json.loads(users_path.read_text())
    assert len(users) == 1
    assert users[0]["role"] == "customer"

@pytest.mark.parametrize("changes", [
    {"name": "   "},
    {"email": "not-an-email"},
    {"password": "short"}
])
def test_invalid_owner_registration(owner_client, changes):
    client, users_path = owner_client

    response = client.post(
        "/restaurant-owners",
        json={**OWNER, **changes}
    )

    assert response.status_code == 422

    users = json.loads(users_path.read_text())
    assert users == []

@pytest.mark.parametrize("extra_field", [
    {"role": "admin"},
    {"restaurant_ids": [1]},
    {"is_active": False}
])
def test_owner_cannot_set_permissions(owner_client, extra_field):
    client, users_path = owner_client

    response = client.post(
        "/restaurant-owners",
        json={**OWNER, **extra_field}
    )

    assert response.status_code == 422

    users = json.loads(users_path.read_text())
    assert users == []

def test_owner_can_login(owner_client):
    client, _ = owner_client

    client.post("/restaurant-owners", json=OWNER)

    response = client.post("/auth/login", json={
        "email": OWNER["email"],
        "password": OWNER["password"]
    })

    assert response.status_code == 200

    token = response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["role"] == "restaurant owner"

def test_owner_can_register_a_restaurant(owner_client):
    client, users_path = owner_client

    response = client.post("/restaurant-owners", json=OWNER)
    assert response.status_code == 201

    owner_id = response.json()["id"]

    response = client.post("/auth/login", json={
        "email": OWNER["email"],
        "password": OWNER["password"]
    })

    assert response.status_code == 200

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/restaurants",
        json=RESTAURANT,
        headers=headers
    )

    assert response.status_code == 201

    restaurant_id = response.json()["id"]

    users = json.loads(users_path.read_text())
    owner = next(user for user in users if user["id"] == owner_id)

    assert restaurant_id in owner["restaurant_ids"]

    response = client.get(
    "/restaurants/mine",
    headers=headers
    )

    assert response.status_code == 200
    assert restaurant_id in [r["id"] for r in response.json()]

    response = client.put(
        f"/restaurants/{restaurant_id}",
        json={"name": "Updated Tacos"},
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Tacos"

    response = client.post(
        f"/restaurants/{restaurant_id}/menu-items",
        json=MENU_ITEM,
        headers=headers
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Veggie Tacos"