from fastapi import APIRouter, Depends, HTTPException

from app.core.config import (
    get_carts_data_path, get_menu_items_data_path,
    get_restaurants_data_path, get_users_data_path,
)
from app.repositories.cart_repository import CartRepository
from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.repositories.user_repository import UserRepository
from app.schemas.cart import CartItemAdd, CartItemUpdate, CartView
from app.services.cart_service import (
    CartService, MenuItemNotFoundError, MenuItemUnavailableError,
    DifferentRestaurantError, ItemNotInCartError,
)
from app.services.customer_rules import CustomerNotFoundError, CustomerInactiveError

router = APIRouter(prefix="/customers/{customer_id}/cart", tags=["cart"])

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


def _call(action):
    try:
        return action()
    except tuple(ERRORS) as exc:
        status, detail = ERRORS[type(exc)]
        raise HTTPException(status_code=status, detail=detail)


@router.get("", response_model=CartView, summary="Get (or create) the active cart", responses=ERROR_DOCS)
def get_cart(customer_id: int, service: CartService = Depends(get_cart_service)):
    return _call(lambda: service.get_cart(customer_id))


@router.post("/items", response_model=CartView, summary="Add an item", responses=ERROR_DOCS)
def add_item(customer_id: int, body: CartItemAdd, service: CartService = Depends(get_cart_service)):
    return _call(lambda: service.add_item(customer_id, body.menu_item_id, body.quantity))


@router.put("/items/{menu_item_id}", response_model=CartView,
            summary="Change an item's quantity", responses=ERROR_DOCS)
def update_item(customer_id: int, menu_item_id: int, body: CartItemUpdate,
                service: CartService = Depends(get_cart_service)):
    return _call(lambda: service.update_quantity(customer_id, menu_item_id, body.quantity))


@router.delete("/items/{menu_item_id}", response_model=CartView,
               summary="Remove an item", responses=ERROR_DOCS)
def remove_item(customer_id: int, menu_item_id: int, service: CartService = Depends(get_cart_service)):
    return _call(lambda: service.remove_item(customer_id, menu_item_id))


@router.delete("", response_model=CartView, summary="Clear the cart", responses=ERROR_DOCS)
def clear_cart(customer_id: int, service: CartService = Depends(get_cart_service)):
    return _call(lambda: service.clear_cart(customer_id))

