from fastapi import APIRouter, Depends, HTTPException

from app.api.routes.cart_support import CustomerId, call, require_cart_owner
from app.core.cart_config import get_carts_data_path
from app.core.config import get_menu_items_data_path, get_restaurants_data_path, get_users_data_path
from app.repositories.cart_repository import CartRepository
from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.repositories.user_repository import UserRepository
from app.schemas.cart import Cart, CartView
from app.services.checkout_service import (
    ActiveCartNotFoundError, CheckoutService, CheckoutValidationError, ValidatedCheckout,
)


router = APIRouter(
    prefix="/customers/{customer_id}/checkout",
    tags=["checkout"],
    dependencies=[Depends(require_cart_owner)],
)

CHECKOUT_ERRORS = {
    401: {"description": "Missing, invalid, or expired token, or inactive account"},
    403: {"description": "Checkout requires access to your own active customer account"},
    404: {"description": "Active cart or customer not found"},
    409: {"description": "The cart is empty or invalid, or the restaurant or an item is unavailable"},
}


def get_checkout_service() -> CheckoutService:
    return CheckoutService(
        CartRepository(get_carts_data_path()),
        MenuItemRepository(get_menu_items_data_path()),
        RestaurantRepository(get_restaurants_data_path()),
        UserRepository(get_users_data_path()),
    )


def validate_or_http_error(service: CheckoutService, customer_id: int) -> ValidatedCheckout:
    """Validate the customer's checkout and turn checkout failures into HTTP errors."""
    try:
        return call(lambda: service.validate(customer_id))
    except ActiveCartNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Active cart not found") from exc
    except CheckoutValidationError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/validate", response_model=Cart, responses=CHECKOUT_ERRORS)
def validate_checkout(customer_id: CustomerId, service: CheckoutService = Depends(get_checkout_service)) -> Cart:
    """Check the active cart against current customer, restaurant, and menu data without placing an order."""
    return validate_or_http_error(service, customer_id).cart


@router.post("/price", response_model=CartView, responses=CHECKOUT_ERRORS)
def price_checkout(customer_id: CustomerId, service: CheckoutService = Depends(get_checkout_service)) -> CartView:
    """Validate the active cart, then return its subtotal, delivery fee, and total recalculated from current menu prices. Nothing is saved and no order is placed."""
    validated = validate_or_http_error(service, customer_id)
    return service.price(validated)

