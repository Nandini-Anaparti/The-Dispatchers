import json


def _add(client, item_id, qty=1, customer=1):
    return client.post(f"/customers/{customer}/cart/items",
                       json={"menu_item_id": item_id, "quantity": qty})


def test_clear_empties_cart_and_zeroes_totals(cart_client):
    _add(cart_client, 1, 2)
    _add(cart_client, 2, 1)
    body = cart_client.delete("/customers/1/cart").json()
    assert body["items"] == []
    assert body["subtotal"] == 0 and body["delivery_fee"] == 0 and body["total"] == 0


def test_clearing_an_empty_cart_is_fine(cart_client):
    assert cart_client.delete("/customers/1/cart").status_code == 200


def test_clear_is_persisted(cart_client, cart_env):
    _add(cart_client, 1)
    cart_client.delete("/customers/1/cart")
    saved = json.loads((cart_env.path / "carts.json").read_text())
    assert saved[0]["items"] == [] and saved[0]["status"] == "active"


def test_clear_does_not_touch_other_customers_carts(cart_client):
    _add(cart_client, 1, customer=1)
    _add(cart_client, 2, customer=3)
    cart_client.delete("/customers/1/cart")
    assert len(cart_client.get("/customers/3/cart").json()["items"]) == 1


def test_cleared_cart_can_start_with_another_restaurant(cart_client):
    _add(cart_client, 1)
    cart_client.delete("/customers/1/cart")
    assert _add(cart_client, 3).status_code == 200


def test_deactivated_customer_rejected(cart_client):
    assert cart_client.delete("/customers/2/cart").status_code == 403

