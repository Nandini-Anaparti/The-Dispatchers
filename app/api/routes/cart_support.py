from fastapi import HTTPException

from app.core.cart_config import get_carts_data_path
from app.core.config import (
    get_menu_items_data_path, get_restaurants_data_path, get_users_data_path,
)
from app.repositories.cart_repository import CartRepository
from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.repositories.user_repository import UserRepository
from app.services.cart_service import (
    CartService, MenuItemNotFoundError, MenuItemUnavailableError,
    DifferentRestaurantError, ItemNotInCartError,
)
from app.services.customer_rules import CustomerNotFoundError, CustomerInactiveError

ERRORS = {
    CustomerNotFoundError: (404, "Customer not found"),
    CustomerInactiveError: (403, "Customer account is deactivated"),
    MenuItemNotFoundError: (404, "Menu item not found"),
    MenuItemUnavailableError: (409, "Menu item is unavailable"),
    DifferentRestaurantError: (409, "Cart can only contain items from one restaurant"),
    ItemNotInCartError: (404, "Item is not in the cart"),
}

ERROR_DOCS = {
    403: {"description": "Customer account is deactivated"},
    404: {"description": "Customer, menu item, or cart entry not found"},
    409: {"description": "Unavailable item, or item from a different restaurant"},
}


def get_cart_service() -> CartService:
    return CartService(
        CartRepository(get_carts_data_path()),
        MenuItemRepository(get_menu_items_data_path()),
        RestaurantRepository(get_restaurants_data_path()),
        UserRepository(get_users_data_path()),
    )


def call(action):
    """Run a service call and turn cart errors into HTTP errors."""
    try:
        return action()
    except tuple(ERRORS) as exc:
        status, detail = ERRORS[type(exc)]
        raise HTTPException(status_code=status, detail=detail)
    