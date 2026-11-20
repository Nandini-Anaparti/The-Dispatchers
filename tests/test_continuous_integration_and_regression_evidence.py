"""Milestone 2 continuous integration and regression evidence for Domenica Vizcaino Andrade."""

import json

import pytest

from tests.orders.test_customer_to_order_workflow import (
    _restaurant,
    edit_menu_item,
    fill_cart,
    sign_up_and_sign_in,
    workflow,
)


def test_menu_update_through_api_is_reflected_in_saved_order(workflow):
    client, _ = workflow
    credentials = {"email": "owner@example.com", "password": "password123"}
    owner = client.post("/restaurant-owners", json={"name": "Owner", **credentials})
    assert owner.status_code == 201
    login = client.post("/auth/login", json=credentials)
    assert login.status_code == 200
    owner_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    restaurant_data = _restaurant(3)
    del restaurant_data["id"]
    restaurant = client.post("/restaurants", json=restaurant_data, headers=owner_headers)
    assert restaurant.status_code == 201
    menu_url = f"/restaurants/{restaurant.json()['id']}/menu-items"
    item_data = {"name": "Soup", "description": "Tomato soup", "price": 10.0, "is_available": True}
    created = client.post(menu_url, json=item_data, headers=owner_headers)
    assert created.status_code == 201
    item = client.get(f"{menu_url}/{created.json()['id']}")
    assert item.status_code == 200
    item_id = item.json()["id"]

    customer_id, headers = sign_up_and_sign_in(client)
    cart_url = f"/customers/{customer_id}/cart"
    cart = client.post(f"{cart_url}/items", json={"menu_item_id": item_id, "quantity": 2}, headers=headers)
    assert cart.status_code == 200
    assert cart.json()["total"] == 22.0

    updated = client.put(f"{menu_url}/{item_id}", json={**item_data, "price": 12.0}, headers=owner_headers)
    assert updated.status_code == 200
    refreshed = client.get(cart_url, headers=headers)
    assert refreshed.status_code == 200
    assert refreshed.json()["total"] == 26.0

    placed = client.post(f"/customers/{customer_id}/checkout", headers=headers)
    assert placed.status_code == 201
    order = placed.json()
    assert order["items"][0]["unit_price"] == 12.0
    assert order["total"] == 26.0
    saved = client.get(f"/customers/{customer_id}/orders/{order['id']}", headers=headers)
    assert saved.status_code == 200
    assert saved.json() == order


@pytest.mark.parametrize("change", ["unavailable", "deactivated", "missing"])
def test_invalidated_menu_item_blocks_order_and_preserves_storage(workflow, change):
    client, path = workflow
    customer_id, headers = sign_up_and_sign_in(client)
    fill_cart(client, customer_id, headers)
    if change == "missing":
        menu_path = path / "menu_items.json"
        menu = json.loads(menu_path.read_text())
        menu_path.write_text(json.dumps([item for item in menu if item["id"] != 2]))
    else:
        flag = "is_available" if change == "unavailable" else "is_active"
        edit_menu_item(path, 2, **{flag: False})

    carts_path = path / "carts.json"
    orders_path = path / "orders.json"
    before = (carts_path.read_bytes(), orders_path.read_bytes())

    response = client.post(f"/customers/{customer_id}/checkout", headers=headers)
    assert response.status_code == 409
    assert "Menu item 2" in response.json()["detail"]
    assert (carts_path.read_bytes(), orders_path.read_bytes()) == before
