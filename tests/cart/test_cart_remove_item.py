import json


def _add(client, item_id, qty=1, customer=1):
    return client.post(f"/customers/{customer}/cart/items",
                       json={"menu_item_id": item_id, "quantity": qty})


def _remove(client, item_id, customer=1):
    return client.delete(f"/customers/{customer}/cart/items/{item_id}")


def test_remove_one_item_keeps_the_others(cart_client):
    _add(cart_client, 1)
    _add(cart_client, 2)
    body = _remove(cart_client, 1).json()
    assert [l["menu_item_id"] for l in body["items"]] == [2]


def test_total_is_recalculated_after_removal(cart_client):
    _add(cart_client, 1)
    _add(cart_client, 2)
    body = _remove(cart_client, 1).json()
    assert body["subtotal"] == 5.0 and body["total"] == 7.0  # 5 item + 2 delivery


def test_removing_missing_item_returns_404(cart_client):
    assert _remove(cart_client, 1).status_code == 404


def test_emptied_cart_can_start_with_another_restaurant(cart_client):
    _add(cart_client, 1)
    _remove(cart_client, 1)
    r = _add(cart_client, 3)
    assert r.status_code == 200 and r.json()["restaurant_id"] == 2


def test_removal_is_persisted(cart_client, cart_env):
    _add(cart_client, 1)
    _add(cart_client, 2)
    _remove(cart_client, 1)
    saved = json.loads((cart_env.path / "carts.json").read_text())
    assert saved[0]["items"] == [{"menu_item_id": 2, "quantity": 1}]


def test_deactivated_customer_rejected(cart_client):
    assert _remove(cart_client, 1, customer=2).status_code == 403
