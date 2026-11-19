import json

import pytest

from app.services.checkout_service import CheckoutService


CART_URL = "/customers/1/cart"
VALIDATE_URL = "/customers/1/checkout/validate"


@pytest.fixture
def checkout_storage(cart_env, monkeypatch):
    carts = cart_env.path / "carts.json"
    orders = cart_env.path / "orders.json"
    orders.write_text("[]", encoding="utf-8")
    monkeypatch.setenv("ORDERS_DATA_PATH", str(orders))
    return carts, orders


def add_item(client, menu_item_id=1):
    response = client.post(f"{CART_URL}/items", json={"menu_item_id": menu_item_id})
    assert response.status_code == 200


def test_valid_checkout_uses_current_menu_and_leaves_storage_unchanged(
    signed_in_cart_client, cart_env, checkout_storage
):
    add_item(signed_in_cart_client)
    add_item(signed_in_cart_client, menu_item_id=2)
    menu = cart_env.menu_repo.get_all()
    menu[0].price = 19.50
    cart_env.menu_repo.save_all(menu)
    before = [path.read_bytes() for path in checkout_storage]

    service = CheckoutService(
        cart_env.cart_repo, cart_env.menu_repo, cart_env.restaurant_repo, cart_env.user_repo
    )
    validated = service.validate(1)
    assert validated.restaurant.id == 1
    assert set(validated.menu_items) == {1, 2}
    assert validated.menu_items[1].price == 19.50

    response = signed_in_cart_client.post(VALIDATE_URL)
    assert response.status_code == 200
    assert response.json() == validated.cart.model_dump()
    assert [path.read_bytes() for path in checkout_storage] == before


@pytest.mark.parametrize("cart_state", ["missing", "empty", "checked_out"])
def test_checkout_requires_a_nonempty_active_cart(signed_in_cart_client, checkout_storage, cart_state):
    carts, _ = checkout_storage
    if cart_state != "missing":
        cart = {"id": 1, "customer_id": 1, "restaurant_id": 1, "status": "active", "items": []}
        if cart_state == "checked_out":
            cart["status"] = "checked_out"
            cart["items"] = [{"menu_item_id": 1, "quantity": 1}]
        carts.write_text(json.dumps([cart]), encoding="utf-8")
    before = [path.read_bytes() for path in checkout_storage]

    response = signed_in_cart_client.post(VALIDATE_URL)
    assert response.status_code == (409 if cart_state == "empty" else 404)
    assert [path.read_bytes() for path in checkout_storage] == before


@pytest.mark.parametrize("change", ["missing", "closed"])
def test_checkout_revalidates_restaurant(signed_in_cart_client, cart_env, checkout_storage, change):
    add_item(signed_in_cart_client)
    path = cart_env.path / "restaurants.json"
    restaurants = json.loads(path.read_text())
    if change == "closed":
        restaurants[0]["is_open"] = False
    else:
        restaurants.pop(0)
    path.write_text(json.dumps(restaurants))
    before = [path.read_bytes() for path in checkout_storage]

    assert signed_in_cart_client.post(VALIDATE_URL).status_code == 409
    assert [path.read_bytes() for path in checkout_storage] == before


@pytest.mark.parametrize("change", ["missing", "unavailable", "inactive", "other_restaurant"])
def test_checkout_revalidates_every_menu_item(signed_in_cart_client, cart_env, checkout_storage, change):
    add_item(signed_in_cart_client)
    add_item(signed_in_cart_client, menu_item_id=2)
    menu = cart_env.menu_repo.get_all()
    if change == "missing":
        menu.pop(1)
    elif change == "unavailable":
        menu[1].is_available = False
    elif change == "inactive":
        menu[1].is_active = False
    else:
        menu[1].restaurant_id = 2
    cart_env.menu_repo.save_all(menu)
    before = [path.read_bytes() for path in checkout_storage]

    response = signed_in_cart_client.post(VALIDATE_URL)
    assert response.status_code == 409
    assert "Menu item 2" in response.json()["detail"]
    assert [path.read_bytes() for path in checkout_storage] == before


@pytest.mark.parametrize("quantity", [0, -1, 1.5, 1.0, True, "2"])
def test_checkout_rejects_invalid_stored_quantities(signed_in_cart_client, checkout_storage, quantity):
    carts, _ = checkout_storage
    cart = {"id": 1, "customer_id": 1, "restaurant_id": 1, "status": "active",
            "items": [{"menu_item_id": 1, "quantity": quantity}]}
    carts.write_text(json.dumps([cart]), encoding="utf-8")
    before = [path.read_bytes() for path in checkout_storage]

    assert signed_in_cart_client.post(VALIDATE_URL).status_code == 409
    assert [path.read_bytes() for path in checkout_storage] == before


@pytest.mark.parametrize(("caller", "owner", "status"), [
    (None, 1, 401), (2, 2, 401), (99, 99, 401), (3, 1, 403), (4, 4, 403),
])
def test_checkout_requires_an_active_authenticated_cart_owner(
    cart_client, cart_auth_headers, checkout_storage, caller, owner, status
):
    before = [path.read_bytes() for path in checkout_storage]
    headers = {} if caller is None else cart_auth_headers(caller)
    response = cart_client.post(f"/customers/{owner}/checkout/validate", headers=headers)

    assert response.status_code == status
    assert [path.read_bytes() for path in checkout_storage] == before
