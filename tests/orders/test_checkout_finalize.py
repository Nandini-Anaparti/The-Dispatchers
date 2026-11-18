"""CHECKOUT-04: finalize checkout only after the order is saved."""

import json

import pytest

from app.services.order_service import CartMismatchError, EmptyOrderError, OrderService


class FailingOrderRepository:
    """Pretends the disk write failed."""

    def add(self, **fields):
        raise OSError("disk full")


def cart_on_disk(env):
    return json.loads((env.path / "carts.json").read_text())[0]


def test_successful_checkout_saves_order_and_closes_cart(order_env, priced_cart):
    service = OrderService(order_env.order_repo, order_env.cart_repo)
    cart = order_env.cart_repo.get_active_by_customer(1)

    order = service.finalize_checkout(cart, priced_cart)

    assert order.id == 1
    assert order_env.order_repo.get_by_id(1) == order       # order saved
    assert cart_on_disk(order_env)["status"] == "checked_out"  # cart closed
    assert order_env.cart_repo.get_active_by_customer(1) is None


def test_failed_order_save_leaves_cart_unchanged(order_env, priced_cart):
    before = cart_on_disk(order_env)
    service = OrderService(FailingOrderRepository(), order_env.cart_repo)
    cart = order_env.cart_repo.get_active_by_customer(1)

    with pytest.raises(OSError):
        service.finalize_checkout(cart, priced_cart)

    assert cart_on_disk(order_env) == before  # still active, same items


def test_empty_cart_is_rejected_and_cart_stays_active(order_env, priced_cart):
    service = OrderService(order_env.order_repo, order_env.cart_repo)
    cart = order_env.cart_repo.get_active_by_customer(1)
    empty = priced_cart.model_copy(update={"items": [], "subtotal": 0, "total": 0})

    with pytest.raises(EmptyOrderError):
        service.finalize_checkout(cart, empty)

    assert cart_on_disk(order_env)["status"] == "active"
    assert order_env.order_repo.get_all() == []


def test_priced_cart_must_match_the_cart(order_env, priced_cart):
    service = OrderService(order_env.order_repo, order_env.cart_repo)
    cart = order_env.cart_repo.get_active_by_customer(1)
    other_customer = priced_cart.model_copy(update={"customer_id": 2})

    with pytest.raises(CartMismatchError):
        service.finalize_checkout(cart, other_customer)
    assert order_env.order_repo.get_all() == []


def test_customer_gets_a_new_empty_cart_after_checkout(order_env, priced_cart):
    service = OrderService(order_env.order_repo, order_env.cart_repo)
    service.finalize_checkout(order_env.cart_repo.get_active_by_customer(1), priced_cart)

    new_cart = order_env.cart_repo.get_or_create_active(1)
    assert new_cart.id == 2
    assert new_cart.items == []
