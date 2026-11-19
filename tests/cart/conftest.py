import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.core.auth import create_access_token
from app.main import app
from app.repositories.cart_repository import CartRepository
from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.repositories.user_repository import UserRepository


def _restaurant(rid, fee):
    return {"id": rid, "name": f"R{rid}", "cuisine": "Italian", "rating": 4.0,
            "delivery_time_minutes": 20, "delivery_fee": fee, "address": "1 Main St", "is_open": True}


def _item(iid, rid, price, available=True):
    return {"id": iid, "restaurant_id": rid, "name": f"Item{iid}", "description": "d",
            "price": price, "is_available": available}


def _user(uid, active=True, role="customer"):
    return {"id": uid, "name": f"U{uid}", "email": f"u{uid}@x.com", "role": role,
            "is_active": active, "delivery_address": "5 Home St", "password_hash": "x"}


@pytest.fixture
def cart_env(tmp_path):
    files = {
        "restaurants.json": [_restaurant(1, 2.0), _restaurant(2, 3.0)],
        "menu.json": [_item(1, 1, 10.0), _item(2, 1, 5.0), _item(3, 2, 8.0), _item(4, 1, 7.0, False)],
        "users.json": [_user(1), _user(2, active=False), _user(3), _user(4, role="admin")],
        "carts.json": [],
    }
    for name, content in files.items():
        (tmp_path / name).write_text(json.dumps(content))
    return SimpleNamespace(
        path=tmp_path,
        cart_repo=CartRepository(tmp_path / "carts.json"),
        menu_repo=MenuItemRepository(tmp_path / "menu.json"),
        restaurant_repo=RestaurantRepository(tmp_path / "restaurants.json"),
        user_repo=UserRepository(tmp_path / "users.json"),
    )


@pytest.fixture
def cart_client(cart_env, monkeypatch):
    monkeypatch.setenv("CARTS_DATA_PATH", str(cart_env.path / "carts.json"))
    monkeypatch.setenv("MENU_ITEMS_DATA_PATH", str(cart_env.path / "menu.json"))
    monkeypatch.setenv("RESTAURANTS_DATA_PATH", str(cart_env.path / "restaurants.json"))
    monkeypatch.setenv("USERS_DATA_PATH", str(cart_env.path / "users.json"))
    monkeypatch.setenv("AUTH_SECRET_KEY", "cart-test-signing-key-for-local-tests-only")
    with TestClient(app) as client:
        yield client


@pytest.fixture
def cart_auth_headers():
    def headers(customer_id):
        return {"Authorization": f"Bearer {create_access_token(customer_id)}"}

    return headers


@pytest.fixture
def signed_in_cart_client(cart_client, cart_auth_headers):
    cart_client.headers.update(cart_auth_headers(1))
    return cart_client
