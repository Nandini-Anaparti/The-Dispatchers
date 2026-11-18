import pytest

from app.repositories.cart_repository import CartRepository
from app.schemas.cart import Cart, CartItem


def test_add_and_find_active_cart(cart_env):
    cart_env.cart_repo.add(Cart(id=1, customer_id=1))
    assert cart_env.cart_repo.get_active_by_customer(1).id == 1
    assert cart_env.cart_repo.get_active_by_customer(2) is None


def test_checked_out_cart_is_not_active(cart_env):
    cart_env.cart_repo.add(Cart(id=1, customer_id=1, status="checked_out"))
    assert cart_env.cart_repo.get_active_by_customer(1) is None


def test_update_replaces_the_stored_cart(cart_env):
    cart_env.cart_repo.add(Cart(id=1, customer_id=1))
    cart_env.cart_repo.update(
        Cart(id=1, customer_id=1, restaurant_id=1, items=[CartItem(menu_item_id=1, quantity=2)]))
    assert cart_env.cart_repo.get_active_by_customer(1).items[0].quantity == 2


def test_update_unknown_cart_returns_none(cart_env):
    assert cart_env.cart_repo.update(Cart(id=99, customer_id=1)) is None


def test_missing_data_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        CartRepository(tmp_path / "nope.json").get_all()