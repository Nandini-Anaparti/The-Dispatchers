import json
import pytest
from argon2 import PasswordHasher
from fastapi.testclient import TestClient
from app.core.auth import create_access_token

NEW_RESTAURANT = {
    "name": "Test Tacos",
    "cuisine": "Mexican",
    "delivery_time_minutes": 20,
    "delivery_fee": 1.99,
    "address": "3 Test St"
}

NEW_MENU_ITEM = {
    "name": "Pasta",
    "description": "Tomato pasta",
    "price": 12.99,
    "is_available": True
}

@pytest.fixture
def role_client(tmp_path, monkeypatch):
    restaurants_path = tmp_path / "restaurants.json"
    menu_path = tmp_path / "menu_items.json"
    users_path = tmp_path / "users.json"

    restaurants = [
        {
            "id": 1,
            "name": "Test Pizza",
            "cuisine": "Italian",
            "rating": 4.5,
            "delivery_time_minutes": 25,
            "delivery_fee": 1.99,
            "address": "1 Test St",
            "is_open": True
        },
        {
            "id": 2,
            "name": "Test Sushi",
            "cuisine": "Japanese",
            "rating": 4.5,
            "delivery_time_minutes": 30,
            "delivery_fee": 2.99,
            "address": "2 Test St",
            "is_open": True
        }
    ]

    menu_items = [
        {
            "id": 1,
            "restaurant_id": 1,
            "name": "Pizza",
            "description": "Cheese pizza",
            "price": 12.99,
            "is_available": True
        },
        {
            "id": 2,
            "restaurant_id": 2,
            "name": "Sushi",
            "description": "Vegetable roll",
            "price": 10.99,
            "is_available": True
        }
    ]

    password_hash = PasswordHasher().hash("test-password-123")

    users = [
        {
            "id": 1,
            "name": "Test Customer",
            "email": "customer@example.com",
            "role": "customer",
            "password_hash": password_hash,
            "restaurant_ids": []
        },
        {
            "id": 2,
            "name": "Restaurant Owner One",
            "email": "owner1@example.com",
            "role": "restaurant owner",
            "password_hash": password_hash,
            "restaurant_ids": [1]
        },
        {
            "id": 3,
            "name": "Restaurant Owner Two",
            "email": "owner2@example.com",
            "role": "restaurant owner",
            "password_hash": password_hash,
            "restaurant_ids": [2]
        },
        {
            "id": 4,
            "name": "Test Admin",
            "email": "admin@example.com",
            "role": "admin",
            "password_hash": password_hash,
            "restaurant_ids": []
        }
    ]

    restaurants_path.write_text(json.dumps(restaurants))
    menu_path.write_text(json.dumps(menu_items))
    users_path.write_text(json.dumps(users))

    monkeypatch.setenv("RESTAURANTS_DATA_PATH", str(restaurants_path))
    monkeypatch.setenv("MENU_ITEMS_DATA_PATH", str(menu_path))
    monkeypatch.setenv("USERS_DATA_PATH", str(users_path))
    monkeypatch.setenv(
        "AUTH_SECRET_KEY",
        "test-only-secret-for-authorization-tests-123456"
    )

    from app.main import app

    with TestClient(app) as client:
        yield client, users_path, restaurants_path, menu_path

def auth_headers(user_id):
    token = create_access_token(user_id)
    return {"Authorization": f"Bearer {token}"}

def test_public_browsing(role_client):
    client, _, _, _ = role_client

    assert client.get("/restaurants").status_code == 200
    assert client.get(
        "/restaurants/1/menu-items"
    ).status_code == 200
    assert client.get("/restaurants/1/menu-items/1").status_code == 200


def test_menu_writes_reject_invalid_bearer_token(role_client):
    client, _, _, menu_path = role_client
    original_menu = menu_path.read_bytes()
    headers = {"Authorization": "Bearer invalid-token"}

    responses = (
        client.post("/restaurants/1/menu-items", json=NEW_MENU_ITEM, headers=headers),
        client.put("/restaurants/1/menu-items/1", json=NEW_MENU_ITEM, headers=headers),
        client.patch("/restaurants/1/menu-items/1/deactivate", headers=headers),
    )
    for response in responses:
        assert response.status_code == 401
        assert response.headers["WWW-Authenticate"] == "Bearer"
    assert menu_path.read_bytes() == original_menu


def test_owner_cannot_modify_foreign_item_under_assigned_restaurant(role_client):
    client, _, _, menu_path = role_client
    original_menu = menu_path.read_bytes()
    headers = auth_headers(2)

    item_url = "/restaurants/1/menu-items/2"
    assert client.put(item_url, json=NEW_MENU_ITEM, headers=headers).status_code == 404
    assert client.patch(f"{item_url}/deactivate", headers=headers).status_code == 404
    assert menu_path.read_bytes() == original_menu

def test_unauthenticated_requests(role_client):
    client, _, _, _ = role_client

    assert client.post(
        "/restaurants",
        json=NEW_RESTAURANT
    ).status_code == 401

    assert client.put(
        "/restaurants/1",
        json={"name": "Changed Name"}
    ).status_code == 401

    assert client.post(
        "/restaurants/1/menu-items",
        json=NEW_MENU_ITEM
    ).status_code == 401

    assert client.put(
        "/restaurants/1/menu-items/1",
        json=NEW_MENU_ITEM
    ).status_code == 401

    assert client.get("/restaurants/mine").status_code == 401

    assert client.get(
    "/restaurants/1/menu-items/manage"
    ).status_code == 401

    assert client.patch(
        "/restaurants/1/menu-items/1/deactivate"
    ).status_code == 401

def test_customer_cannot_manage_restaurants(role_client):
    client, _, restaurants_path, menu_path = role_client

    headers = auth_headers(1)

    original_restaurants = restaurants_path.read_text()
    original_menu = menu_path.read_text()

    assert client.post(
        "/restaurants",
        json=NEW_RESTAURANT,
        headers=headers
    ).status_code == 403

    assert client.put(
        "/restaurants/1",
        json={"name": "Changed Name"},
        headers=headers
    ).status_code == 403

    assert client.post(
        "/restaurants/1/menu-items",
        json=NEW_MENU_ITEM,
        headers=headers
    ).status_code == 403

    assert client.put(
        "/restaurants/1/menu-items/1",
        json=NEW_MENU_ITEM,
        headers=headers
    ).status_code == 403

    assert client.get(
        "/restaurants/mine",
        headers=headers
    ).status_code == 403

    assert client.get(
    "/restaurants/1/menu-items/manage",
    headers=headers
    ).status_code == 403

    assert client.patch(
        "/restaurants/1/menu-items/1/deactivate",
        headers=headers
    ).status_code == 403

    assert restaurants_path.read_text() == original_restaurants
    assert menu_path.read_text() == original_menu

def test_owner_can_manage_assigned_restaurant(role_client):
    client, _, _, _ = role_client

    headers = auth_headers(2)

    response = client.put(
        "/restaurants/1",
        json={"name": "Updated Pizza"},
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Pizza"

    response = client.post(
        "/restaurants/1/menu-items",
        json=NEW_MENU_ITEM,
        headers=headers
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Pasta"

    response = client.put(
        "/restaurants/1/menu-items/1",
        json=NEW_MENU_ITEM,
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Pasta"

    response = client.patch(
    "/restaurants/1/menu-items/1/deactivate",
    headers=headers
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False

def test_owner_cannot_manage_other_restaurant(role_client):
    client, _, restaurants_path, menu_path = role_client

    headers = auth_headers(2)

    original_restaurants = restaurants_path.read_text()
    original_menu = menu_path.read_text()

    assert client.put(
        "/restaurants/2",
        json={"name": "Changed Sushi"},
        headers=headers
    ).status_code == 403

    assert client.post(
        "/restaurants/2/menu-items",
        json=NEW_MENU_ITEM,
        headers=headers
    ).status_code == 403

    assert client.put(
        "/restaurants/2/menu-items/2",
        json=NEW_MENU_ITEM,
        headers=headers
    ).status_code == 403

    assert client.get(
    "/restaurants/2/menu-items/manage",
    headers=headers
    ).status_code == 403

    assert client.patch(
        "/restaurants/2/menu-items/2/deactivate",
        headers=headers
    ).status_code == 403

    assert restaurants_path.read_text() == original_restaurants
    assert menu_path.read_text() == original_menu

def test_owner_can_create_restaurant(role_client):
    client, users_path, _, _ = role_client

    headers = auth_headers(2)

    response = client.post(
        "/restaurants",
        json=NEW_RESTAURANT,
        headers=headers
    )

    assert response.status_code == 201

    new_restaurant = response.json()
    restaurant_id = new_restaurant["id"]

    assert new_restaurant["name"] == "Test Tacos"

    users = json.loads(users_path.read_text())

    owner = next(user for user in users if user["id"] == 2)

    assert restaurant_id in owner["restaurant_ids"]

    response = client.get(
        "/restaurants/mine",
        headers=headers
    )

    assert response.status_code == 200
    assert [r["id"] for r in response.json()] == [1, restaurant_id]

    response = client.put(
        f"/restaurants/{restaurant_id}",
        json={"name": "Updated Tacos"},
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Tacos"

    response = client.post(
        f"/restaurants/{restaurant_id}/menu-items",
        json=NEW_MENU_ITEM,
        headers=headers
    )

    assert response.status_code == 201

def test_admin_can_manage_restaurants(role_client):
    client, _, _, _ = role_client

    headers = auth_headers(4)

    response = client.post(
        "/restaurants",
        json=NEW_RESTAURANT,
        headers=headers
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Test Tacos"
    
    new_restaurant_id = response.json()["id"]

    response = client.get(
        "/restaurants/mine",
        headers=headers
    )

    assert response.status_code == 200
    assert [r["id"] for r in response.json()] == [
        1, 2, new_restaurant_id
    ]

    response = client.put(
        "/restaurants/2",
        json={"name": "Updated Sushi"},
        headers=headers
    )

    assert response.status_code == 200

    response = client.post(
        "/restaurants/2/menu-items",
        json=NEW_MENU_ITEM,
        headers=headers
    )

    assert response.status_code == 201

    response = client.put(
        "/restaurants/2/menu-items/2",
        json=NEW_MENU_ITEM,
        headers=headers
    )

    assert response.status_code == 200

def test_user_cannot_choose_admin_role(role_client):
    client, users_path, _, _ = role_client

    response = client.post("/customers", json={
        "name": "New Customer",
        "email": "newcustomer@example.com",
        "password": "secure-password-123",
        "role": "admin",
        "restaurant_ids": [1]
    })

    assert response.status_code == 201
    assert response.json()["role"] == "customer"

    users = json.loads(users_path.read_text())

    assert users[-1]["role"] == "customer"
    assert users[-1]["restaurant_ids"] == []

    login_response = client.post("/auth/login", json={
        "email": "newcustomer@example.com",
        "password": "secure-password-123"
    })

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/restaurants",
        json=NEW_RESTAURANT,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403

def test_deactivated_owner_cannot_manage(role_client):
    client, users_path, _, _ = role_client

    users = json.loads(users_path.read_text())
    users[1]["is_active"] = False

    users_path.write_text(json.dumps(users))

    response = client.put(
        "/restaurants/1",
        json={"name": "Changed Name"},
        headers=auth_headers(2)
    )

    assert response.status_code == 401

def test_authenticated_user_can_view_own_account(role_client):
    client, _, _, _ = role_client

    response = client.get(
        "/auth/me",
        headers=auth_headers(2)
    )

    assert response.status_code == 200
    assert response.json()["id"] == 2
    assert response.json()["role"] == "restaurant owner"
    assert "password_hash" not in response.json()
    assert "restaurant_ids" not in response.json()
