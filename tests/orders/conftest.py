"""Shared setup for checkout and order tests. Every test uses temporary JSON files."""

import json
from types import SimpleNamespace

import pytest

from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.cart import CartLine, CartView


def _restaurant(rid):
    return {"id": rid, "name": f"R{rid}", "cuisine": "Italian", "rating": 4.0,
            "delivery_time_minutes": 20, "delivery_fee": 2.0, "address": "1 Main St", "is_open": True}


def _item(iid, rid, price):
    return {"id": iid, "restaurant_id": rid, "name": f"Item{iid}", "description": "d",
            "price": price, "is_available": True}


def _user(uid, role="customer", restaurant_ids=()):
    return {"id": uid, "name": f"U{uid}", "email": f"u{uid}@x.com", "role": role,
            "is_active": True, "delivery_address": "5 Home St", "password_hash": "x",
            "restaurant_ids": list(restaurant_ids)}


@pytest.fixture
def order_env(tmp_path, monkeypatch):
    files = {
        "restaurants.json": [_restaurant(1)],
        "menu_items.json": [_item(1, 1, 10.0), _item(2, 1, 5.0)],
        "users.json": [_user(1), _user(2), _user(9, role="admin"),
                       # 5 owns restaurant 1, 6 owns a different restaurant
                       _user(5, role="restaurant owner", restaurant_ids=[1]),
                       _user(6, role="restaurant owner", restaurant_ids=[2])],
        # customer 1 has an active cart with 2 x Item1 and 1 x Item2
        "carts.json": [{"id": 1, "customer_id": 1, "restaurant_id": 1, "status": "active",
                        "items": [{"menu_item_id": 1, "quantity": 2},
                                  {"menu_item_id": 2, "quantity": 1}]}],
        "orders.json": [],
    }
    for name, content in files.items():
        (tmp_path / name).write_text(json.dumps(content), encoding="utf-8")

    monkeypatch.setenv("RESTAURANTS_DATA_PATH", str(tmp_path / "restaurants.json"))
    monkeypatch.setenv("MENU_ITEMS_DATA_PATH", str(tmp_path / "menu_items.json"))
    monkeypatch.setenv("USERS_DATA_PATH", str(tmp_path / "users.json"))
    monkeypatch.setenv("CARTS_DATA_PATH", str(tmp_path / "carts.json"))
    monkeypatch.setenv("ORDERS_DATA_PATH", str(tmp_path / "orders.json"))
    monkeypatch.setenv("AUTH_SECRET_KEY", "order-test-signing-key-for-local-tests-only")
    return SimpleNamespace(
        path=tmp_path,
        order_repo=OrderRepository(tmp_path / "orders.json"),
        cart_repo=CartRepository(tmp_path / "carts.json"),
    )


@pytest.fixture
def priced_cart():
    """What CHECKOUT-01/02 hand over: a validated cart with current prices and backend totals."""
    return CartView(
        id=1, customer_id=1, restaurant_id=1, status="active",
        items=[
            CartLine(menu_item_id=1, name="Item1", unit_price=10.0, quantity=2, line_total=20.0),
            CartLine(menu_item_id=2, name="Item2", unit_price=5.0, quantity=1, line_total=5.0),
        ],
        subtotal=25.0, delivery_fee=2.0, total=27.0,
    )
