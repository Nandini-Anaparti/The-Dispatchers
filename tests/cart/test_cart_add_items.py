import json
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier


def _add(client, item_id, qty=1):
    return client.post("/customers/1/cart/items", json={"menu_item_id": item_id, "quantity": qty})


def test_add_available_item(signed_in_cart_client):
    r = _add(signed_in_cart_client, 1, 2)
    assert r.status_code == 200
    body = r.json()
    assert body["restaurant_id"] == 1 and body["items"][0]["quantity"] == 2
    assert body["subtotal"] == 20.0


def test_quantity_defaults_to_one(signed_in_cart_client):
    r = signed_in_cart_client.post("/customers/1/cart/items", json={"menu_item_id": 1})
    assert r.json()["items"][0]["quantity"] == 1


def test_adding_same_item_updates_quantity_instead_of_duplicating(signed_in_cart_client):
    _add(signed_in_cart_client, 1, 1)
    body = _add(signed_in_cart_client, 1, 2).json()
    assert len(body["items"]) == 1 and body["items"][0]["quantity"] == 3


def test_invalid_quantities_rejected(signed_in_cart_client):
    assert _add(signed_in_cart_client, 1, 0).status_code == 422
    assert _add(signed_in_cart_client, 1, -1).status_code == 422


def test_unavailable_item_rejected(signed_in_cart_client):
    assert _add(signed_in_cart_client, 4).status_code == 409


def test_nonexistent_item_rejected(signed_in_cart_client):
    assert _add(signed_in_cart_client, 99).status_code == 404


def test_cannot_mix_restaurants_and_cart_stays_unchanged(signed_in_cart_client):
    _add(signed_in_cart_client, 1)
    assert _add(signed_in_cart_client, 3).status_code == 409
    cart = signed_in_cart_client.get("/customers/1/cart").json()
    assert len(cart["items"]) == 1 and cart["restaurant_id"] == 1


def test_deactivated_and_unknown_customers_rejected(cart_client, cart_auth_headers):
    for customer_id in (2, 99):
        response = cart_client.post(
            f"/customers/{customer_id}/cart/items",
            json={"menu_item_id": 1},
            headers=cart_auth_headers(customer_id),
        )
        assert response.status_code == 401


def test_added_items_are_persisted(signed_in_cart_client, cart_env):
    _add(signed_in_cart_client, 1, 2)
    saved = json.loads((cart_env.path / "carts.json").read_text())
    assert saved[0]["items"] == [{"menu_item_id": 1, "quantity": 2}]


def test_rejected_items_do_not_create_a_cart(signed_in_cart_client, cart_env):
    menu_path = cart_env.path / "menu.json"
    menu = json.loads(menu_path.read_text())
    menu[0]["is_active"] = False
    menu_path.write_text(json.dumps(menu))

    assert _add(signed_in_cart_client, 1).status_code == 409
    assert _add(signed_in_cart_client, 4).status_code == 409
    assert _add(signed_in_cart_client, 99).status_code == 404
    assert cart_env.cart_repo.get_all() == []


def test_concurrent_additions_both_persist(signed_in_cart_client, cart_env):
    ready = Barrier(2, timeout=5)

    def add_item(item_id):
        ready.wait()
        _add(signed_in_cart_client, item_id).raise_for_status()

    with ThreadPoolExecutor(max_workers=2) as executor:
        list(executor.map(add_item, (1, 2)))

    cart, = cart_env.cart_repo.get_all()
    assert {item.menu_item_id: item.quantity for item in cart.items} == {1: 1, 2: 1}
