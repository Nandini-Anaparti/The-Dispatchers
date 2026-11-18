import json


def _add(client, item_id, qty=1, customer=1):
    return client.post(f"/customers/{customer}/cart/items",
                       json={"menu_item_id": item_id, "quantity": qty})


def test_add_available_item(cart_client):
    r = _add(cart_client, 1, 2)
    assert r.status_code == 200
    body = r.json()
    assert body["restaurant_id"] == 1 and body["items"][0]["quantity"] == 2
    assert body["subtotal"] == 20.0


def test_quantity_defaults_to_one(cart_client):
    r = cart_client.post("/customers/1/cart/items", json={"menu_item_id": 1})
    assert r.json()["items"][0]["quantity"] == 1


def test_adding_same_item_updates_quantity_instead_of_duplicating(cart_client):
    _add(cart_client, 1, 1)
    body = _add(cart_client, 1, 2).json()
    assert len(body["items"]) == 1 and body["items"][0]["quantity"] == 3


def test_invalid_quantities_rejected(cart_client):
    assert _add(cart_client, 1, 0).status_code == 422
    assert _add(cart_client, 1, -1).status_code == 422


def test_unavailable_item_rejected(cart_client):
    assert _add(cart_client, 4).status_code == 409


def test_nonexistent_item_rejected(cart_client):
    assert _add(cart_client, 99).status_code == 404


def test_cannot_mix_restaurants_and_cart_stays_unchanged(cart_client):
    _add(cart_client, 1)
    assert _add(cart_client, 3).status_code == 409
    cart = cart_client.get("/customers/1/cart").json()
    assert len(cart["items"]) == 1 and cart["restaurant_id"] == 1


def test_deactivated_and_unknown_customers_rejected(cart_client):
    assert _add(cart_client, 1, customer=2).status_code == 403
    assert _add(cart_client, 1, customer=99).status_code == 404


def test_added_items_are_persisted(cart_client, cart_env):
    _add(cart_client, 1, 2)
    saved = json.loads((cart_env.path / "carts.json").read_text())
    assert saved[0]["items"] == [{"menu_item_id": 1, "quantity": 2}]
