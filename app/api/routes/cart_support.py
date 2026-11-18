from fastapi import Depends, HTTPException

from app.core.auth import get_current_user
from app.core.cart_config import get_carts_data_path
from app.core.config import (
    get_menu_items_data_path, get_restaurants_data_path, get_users_data_path,
)
from app.repositories.cart_repository import CartRepository
from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserInDB
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
    401: {"description": "Missing or invalid authentication, or inactive account"},
    403: {"description": "Cart access is limited to its customer"},
    404: {"description": "Customer, menu item, or cart entry not found"},
    409: {"description": "Unavailable item, or item from a different restaurant"},
}


def require_cart_owner(
    customer_id: int, current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    if current_user.role != "customer" or current_user.id != customer_id:
        raise HTTPException(status_code=403, detail="You can only access your own cart")
    return current_user


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
        raise HTTPException(status_code=status, detail=detail) from exc
