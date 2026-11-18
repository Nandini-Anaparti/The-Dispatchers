import json


def _add(client, item_id, qty=1, customer=1):
    return client.post(f"/customers/{customer}/cart/items",
                       json={"menu_item_id": item_id, "quantity": qty})


def _update(client, item_id, qty, customer=1):
    return client.put(f"/customers/{customer}/cart/items/{item_id}", json={"quantity": qty})


def test_update_quantity_recalculates_total(cart_client):
    _add(cart_client, 1, 1)
    body = _update(cart_client, 1, 4).json()
    assert body["items"][0]["quantity"] == 4
    assert body["subtotal"] == 40.0 and body["total"] == 42.0


def test_other_items_are_unaffected(cart_client):
    _add(cart_client, 1, 1)
    _add(cart_client, 2, 1)
    body = _update(cart_client, 1, 3).json()
    quantities = {l["menu_item_id"]: l["quantity"] for l in body["items"]}
    assert quantities == {1: 3, 2: 1}


def test_invalid_quantity_rejected(cart_client):
    _add(cart_client, 1, 1)
    assert _update(cart_client, 1, 0).status_code == 422
    assert _update(cart_client, 1, -2).status_code == 422


def test_item_not_in_cart_returns_404(cart_client):
    assert _update(cart_client, 1, 2).status_code == 404


def test_update_is_persisted(cart_client, cart_env):
    _add(cart_client, 1, 1)
    _update(cart_client, 1, 5)
    saved = json.loads((cart_env.path / "carts.json").read_text())
    assert saved[0]["items"] == [{"menu_item_id": 1, "quantity": 5}]


def test_deactivated_customer_rejected(cart_client):
    assert _update(cart_client, 1, 2, customer=2).status_code == 403
