"""CHECKOUT-03: create and persist a complete order snapshot."""

import json

import pytest

from app.repositories.order_repository import OrderRepository
from app.services.order_service import EmptyOrderError, OrderService


def test_order_stores_customer_restaurant_items_total_and_status(order_env, priced_cart):
    order = OrderService(order_env.order_repo).create_order(priced_cart)
    assert order.customer_id == 1
    assert order.restaurant_id == 1
    assert [(i.menu_item_id, i.quantity, i.unit_price) for i in order.items] == [(1, 2, 10.0), (2, 1, 5.0)]
    assert order.subtotal == 25.0
    assert order.delivery_fee == 2.0
    assert order.total == 27.0
    assert order.status == "placed"


def test_order_is_saved_to_json(order_env, priced_cart):
    OrderService(order_env.order_repo).create_order(priced_cart)
    saved = json.loads((order_env.path / "orders.json").read_text())
    assert len(saved) == 1
    assert saved[0]["total"] == 27.0


def test_each_order_gets_a_unique_id(order_env, priced_cart):
    service = OrderService(order_env.order_repo)
    ids = [service.create_order(priced_cart).id for _ in range(3)]
    assert ids == [1, 2, 3]


def test_order_survives_restart(order_env, priced_cart):
    order = OrderService(order_env.order_repo).create_order(priced_cart)
    # A brand-new repository is like restarting the app: it only has the JSON file
    reloaded = OrderRepository(order_env.path / "orders.json").get_by_id(order.id)
    assert reloaded == order


def test_snapshot_keeps_checkout_time_price(order_env, priced_cart):
    order = OrderService(order_env.order_repo).create_order(priced_cart)
    # The menu price changes after the order was placed
    menu = json.loads((order_env.path / "menu_items.json").read_text())
    menu[0]["price"] = 99.0
    (order_env.path / "menu_items.json").write_text(json.dumps(menu))

    reloaded = OrderRepository(order_env.path / "orders.json").get_by_id(order.id)
    assert reloaded.items[0].unit_price == 10.0
    assert reloaded.total == 27.0


def test_empty_cart_does_not_create_an_order(order_env, priced_cart):
    empty = priced_cart.model_copy(update={"items": [], "subtotal": 0, "total": 0})
    with pytest.raises(EmptyOrderError):
        OrderService(order_env.order_repo).create_order(empty)
    assert order_env.order_repo.get_all() == []
