import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.routes.cart_support import get_cart_service
from app.main import app
from app.repositories.cart_repository import CartRepository
from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.repositories.user_repository import UserRepository
from app.services.cart_service import CartService


def _restaurant(rid, fee):
    return {"id": rid, "name": f"R{rid}", "cuisine": "Italian", "rating": 4.0,
            "delivery_time_minutes": 20, "delivery_fee": fee, "address": "1 Main St", "is_open": True}


def _item(iid, rid, price, available=True):
    return {"id": iid, "restaurant_id": rid, "name": f"Item{iid}", "description": "d",
            "price": price, "is_available": available}


def _user(uid, active=True):
    return {"id": uid, "name": f"U{uid}", "email": f"u{uid}@x.com", "role": "customer",
            "is_active": active, "delivery_address": "5 Home St", "password_hash": "x"}


@pytest.fixture
def cart_env(tmp_path):
    files = {
        "restaurants.json": [_restaurant(1, 2.0), _restaurant(2, 3.0)],
        "menu.json": [_item(1, 1, 10.0), _item(2, 1, 5.0), _item(3, 2, 8.0), _item(4, 1, 7.0, False)],
        "users.json": [_user(1), _user(2, active=False), _user(3)],
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
def cart_client(cart_env):
    app.dependency_overrides[get_cart_service] = lambda: CartService(
        cart_env.cart_repo, cart_env.menu_repo, cart_env.restaurant_repo, cart_env.user_repo)
    yield TestClient(app)
    app.dependency_overrides.clear()
    