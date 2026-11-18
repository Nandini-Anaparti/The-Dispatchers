import pytest
from pydantic import ValidationError

from app.schemas.cart import CartItem, CartItemAdd, CartItemUpdate


def test_cart_item_rejects_zero_quantity():
    with pytest.raises(ValidationError):
        CartItem(menu_item_id=1, quantity=0)


def test_add_request_defaults_quantity_to_one():
    assert CartItemAdd(menu_item_id=1).quantity == 1


def test_update_request_rejects_negative_quantity():
    with pytest.raises(ValidationError):
        CartItemUpdate(quantity=-2)

