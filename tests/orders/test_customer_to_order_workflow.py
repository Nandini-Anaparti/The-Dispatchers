"""Integrated workflow: Customer -> Restaurant -> Menu -> Cart -> Checkout -> Order.

Everything goes through the real API, routes, services and repositories, using
temporary JSON files (the committed data/ files are never changed).
"""

import json

import pytest
from fastapi.testclient import TestClient

from app.main import app


def _restaurant(rid, fee=2.0, is_open=True):
    return {"id": rid, "name": f"R{rid}", "cuisine": "Italian", "rating": 4.0,
            "delivery_time_minutes": 20, "delivery_fee": fee, "address": "1 Main St", "is_open": is_open}


def _item(iid, rid, price, available=True):
    return {"id": iid, "restaurant_id": rid, "name": f"Item{iid}", "description": "d",
            "price": price, "is_available": available, "is_active": True}


@pytest.fixture
def workflow(tmp_path, monkeypatch):
    files = {
        "restaurants.json": [_restaurant(1), _restaurant(2, fee=3.0)],
        "menu_items.json": [_item(1, 1, 10.0), _item(2, 1, 5.0), _item(3, 2, 8.0)],
        "users.json": [],
        "carts.json": [],
        "orders.json": [],
    }
    for name, content in files.items():
        (tmp_path / name).write_text(json.dumps(content), encoding="utf-8")
    monkeypatch.setenv("RESTAURANTS_DATA_PATH", str(tmp_path / "restaurants.json"))
    monkeypatch.setenv("MENU_ITEMS_DATA_PATH", str(tmp_path / "menu_items.json"))
    monkeypatch.setenv("USERS_DATA_PATH", str(tmp_path / "users.json"))
    monkeypatch.setenv("CARTS_DATA_PATH", str(tmp_path / "carts.json"))
    monkeypatch.setenv("ORDERS_DATA_PATH", str(tmp_path / "orders.json"))
    monkeypatch.setenv("AUTH_SECRET_KEY", "workflow-test-signing-key-for-local-tests-only")

    with TestClient(app) as client:
        yield client, tmp_path


def sign_up_and_sign_in(client, email="sam@example.com"):
    """Customer step: register a real account, then log in to get a token."""
    registered = client.post("/customers", json={
        "name": "Sam", "email": email, "password": "password123", "delivery_address": "5 Home St",
    })
    assert registered.status_code == 201
    token = client.post("/auth/login", json={"email": email, "password": "password123"}).json()["access_token"]
    return registered.json()["id"], {"Authorization": f"Bearer {token}"}


def edit_menu_item(path, item_id, **changes):
    menu = json.loads((path / "menu_items.json").read_text())
    for item in menu:
        if item["id"] == item_id:
            item.update(changes)
    (path / "menu_items.json").write_text(json.dumps(menu))


def fill_cart(client, customer_id, headers):
    """Restaurant -> Menu -> Cart steps."""
    assert any(r["id"] == 1 for r in client.get("/restaurants").json())
    menu = client.get("/restaurants/1/menu-items").json()
    assert {item["id"] for item in menu} >= {1, 2}
    client.post(f"/customers/{customer_id}/cart/items", json={"menu_item_id": 1, "quantity": 2}, headers=headers)
    cart = client.post(f"/customers/{customer_id}/cart/items", json={"menu_item_id": 2, "quantity": 1},
                       headers=headers)
    assert cart.status_code == 200
    return cart.json()


# ---- The full happy path ----

def test_customer_to_order_full_workflow(workflow):
    client, path = workflow
    customer_id, headers = sign_up_and_sign_in(client)
    cart = fill_cart(client, customer_id, headers)
    assert cart["total"] == 27.0  # 2 x 10 + 5 + 2 delivery, calculated by the backend

    placed = client.post(f"/customers/{customer_id}/checkout", headers=headers)
    assert placed.status_code == 201
    order = placed.json()
    assert order["status"] == "placed"
    assert order["customer_id"] == customer_id
    assert order["restaurant_id"] == 1
    assert [(i["menu_item_id"], i["quantity"], i["unit_price"]) for i in order["items"]] == [(1, 2, 10.0), (2, 1, 5.0)]
    assert order["total"] == 27.0

    # Order step: the customer can see it, and the cart is now empty
    fetched = client.get(f"/customers/{customer_id}/orders/{order['id']}", headers=headers)
    assert fetched.json() == order
    assert client.get(f"/customers/{customer_id}/cart", headers=headers).json()["items"] == []


def test_order_and_relationships_survive_restart(workflow):
    client, path = workflow
    customer_id, headers = sign_up_and_sign_in(client)
    fill_cart(client, customer_id, headers)
    order = client.post(f"/customers/{customer_id}/checkout", headers=headers).json()

    with TestClient(app) as restarted:  # fresh app, only the JSON files remain
        history = restarted.get(f"/customers/{customer_id}/orders", headers=headers).json()
    assert [o["id"] for o in history] == [order["id"]]
    saved_cart = json.loads((path / "carts.json").read_text())[0]
    assert saved_cart["customer_id"] == customer_id
    assert saved_cart["status"] == "checked_out"


# ---- Revalidation and failure cases ----

def test_price_change_before_checkout_uses_current_price(workflow):
    client, path = workflow
    customer_id, headers = sign_up_and_sign_in(client)
    fill_cart(client, customer_id, headers)
    edit_menu_item(path, 1, price=12.0)  # restaurant changes the price after it was added

    order = client.post(f"/customers/{customer_id}/checkout", headers=headers).json()
    assert order["items"][0]["unit_price"] == 12.0
    assert order["total"] == 31.0  # 2 x 12 + 5 + 2


def test_item_unavailable_before_checkout_blocks_order_and_keeps_cart(workflow):
    client, path = workflow
    customer_id, headers = sign_up_and_sign_in(client)
    fill_cart(client, customer_id, headers)
    edit_menu_item(path, 2, is_available=False)

    response = client.post(f"/customers/{customer_id}/checkout", headers=headers)
    assert response.status_code == 409
    assert json.loads((path / "orders.json").read_text()) == []  # no order saved
    cart = client.get(f"/customers/{customer_id}/cart", headers=headers).json()
    assert len(cart["items"]) == 2  # customer keeps their items


def test_empty_cart_cannot_be_checked_out(workflow):
    client, path = workflow
    customer_id, headers = sign_up_and_sign_in(client)
    client.get(f"/customers/{customer_id}/cart", headers=headers)  # creates an empty active cart
    assert client.post(f"/customers/{customer_id}/checkout", headers=headers).status_code == 409


def test_deactivated_customer_cannot_check_out(workflow):
    client, path = workflow
    customer_id, headers = sign_up_and_sign_in(client)
    fill_cart(client, customer_id, headers)
    assert client.post("/customers/me/deactivate", headers=headers).status_code == 204

    response = client.post(f"/customers/{customer_id}/checkout", headers=headers)
    assert response.status_code in (401, 403)
    assert json.loads((path / "orders.json").read_text()) == []


def test_cannot_check_out_another_customers_cart(workflow):
    client, path = workflow
    first_id, first_headers = sign_up_and_sign_in(client, "a@example.com")
    _, second_headers = sign_up_and_sign_in(client, "b@example.com")
    fill_cart(client, first_id, first_headers)
    assert client.post(f"/customers/{first_id}/checkout", headers=second_headers).status_code == 403


def test_checkout_without_token_returns_401(workflow):
    client, path = workflow
    customer_id, _ = sign_up_and_sign_in(client)
    assert client.post(f"/customers/{customer_id}/checkout").status_code == 401


def test_second_checkout_needs_a_new_cart(workflow):
    client, path = workflow
    customer_id, headers = sign_up_and_sign_in(client)
    fill_cart(client, customer_id, headers)
    client.post(f"/customers/{customer_id}/checkout", headers=headers)
    # The old cart is closed, so checking out again has nothing to order
    assert client.post(f"/customers/{customer_id}/checkout", headers=headers).status_code in (404, 409)
    assert len(json.loads((path / "orders.json").read_text())) == 1
