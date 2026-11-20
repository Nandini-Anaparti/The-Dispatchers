"""CHECKOUT-02: recalculate prices and totals from current menu data."""

import json

import pytest

from app.schemas.cart import Cart, CartItem
from app.services.checkout_service import CheckoutService
from app.services.pricing import price_cart

URL = "/customers/1/checkout/price"


def add_item(client, menu_item_id=1, quantity=1):
    response = client.post(
        "/customers/1/cart/items", json={"menu_item_id": menu_item_id, "quantity": quantity}
    )
    assert response.status_code == 200


def set_price(env, item_id, price):
    menu = env.menu_repo.get_all()
    next(item for item in menu if item.id == item_id).price = price
    env.menu_repo.save_all(menu)


def test_price_returns_backend_subtotal_delivery_fee_and_total(signed_in_cart_client):
    add_item(signed_in_cart_client, 1, 2)
    add_item(signed_in_cart_client, 2, 1)

    response = signed_in_cart_client.post(URL)

    assert response.status_code == 200
    body = response.json()
    assert body["subtotal"] == 25.0 and body["delivery_fee"] == 2.0 and body["total"] == 27.0
    lines = [(i["menu_item_id"], i["unit_price"], i["quantity"], i["line_total"]) for i in body["items"]]
    assert lines == [(1, 10.0, 2, 20.0), (2, 5.0, 1, 5.0)]


def test_price_uses_current_menu_price_after_a_change(signed_in_cart_client, cart_env):
    add_item(signed_in_cart_client, 1, 2)
    before = signed_in_cart_client.post(URL).json()

    set_price(cart_env, 1, 12.5)
    after = signed_in_cart_client.post(URL).json()

    assert before["total"] == 22.0  # 2 x 10.00 + 2.00 delivery
    assert after["items"][0]["unit_price"] == 12.5
    assert after["subtotal"] == 25.0 and after["total"] == 27.0


def test_cart_file_stores_no_prices_and_pricing_does_not_write(signed_in_cart_client, cart_env):
    add_item(signed_in_cart_client, 1, 2)
    path = cart_env.path / "carts.json"
    before = path.read_bytes()

    signed_in_cart_client.post(URL)

    assert path.read_bytes() == before
    assert json.loads(before)[0]["items"] == [{"menu_item_id": 1, "quantity": 2}]


def test_totals_sent_by_the_client_are_ignored(signed_in_cart_client):
    add_item(signed_in_cart_client, 1, 1)

    response = signed_in_cart_client.post(URL, json={"subtotal": 0.01, "total": 0.01, "unit_price": 0.01})

    assert response.status_code == 200
    assert response.json()["total"] == 12.0  # 10.00 item + 2.00 delivery


def test_pricing_still_requires_a_valid_checkout(signed_in_cart_client, cart_env):
    assert signed_in_cart_client.post(URL).status_code == 404  # no active cart
    add_item(signed_in_cart_client, 1)
    menu = cart_env.menu_repo.get_all()
    menu[0].is_available = False
    cart_env.menu_repo.save_all(menu)

    assert signed_in_cart_client.post(URL).status_code == 409


@pytest.mark.parametrize(("caller", "status"), [(None, 401), (2, 401), (3, 403), (4, 403)])
def test_pricing_requires_the_cart_owner(cart_client, cart_auth_headers, caller, status):
    headers = {} if caller is None else cart_auth_headers(caller)
    assert cart_client.post(URL, headers=headers).status_code == status


def test_price_cart_skips_missing_menu_items_and_charges_no_fee_when_empty():
    cart = Cart(id=1, customer_id=1, restaurant_id=1, items=[CartItem(menu_item_id=1, quantity=1)])

    priced = price_cart(cart, {}, 2.0)

    assert priced.items == [] and priced.delivery_fee == 0 and priced.total == 0


def test_checkout_service_prices_a_validated_cart_from_current_menu(signed_in_cart_client, cart_env):
    add_item(signed_in_cart_client, 1, 3)
    set_price(cart_env, 1, 11.0)
    service = CheckoutService(
        cart_env.cart_repo, cart_env.menu_repo, cart_env.restaurant_repo, cart_env.user_repo
    )

    priced = service.price(service.validate(1))

    assert priced.subtotal == 33.0 and priced.total == 35.0


def test_cart_view_and_checkout_pricing_agree(signed_in_cart_client):
    """Regression: the cart page and checkout must always show the same totals."""
    add_item(signed_in_cart_client, 1, 2)
    add_item(signed_in_cart_client, 2, 3)

    cart_view = signed_in_cart_client.get("/customers/1/cart").json()
    checkout_view = signed_in_cart_client.post(URL).json()

    assert cart_view == checkout_view
    