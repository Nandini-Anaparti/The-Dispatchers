from fastapi import APIRouter, Depends, HTTPException

from app.api.routes.cart_support import CustomerId, call, require_cart_owner
from app.core.cart_config import get_carts_data_path
from app.core.config import get_menu_items_data_path, get_restaurants_data_path, get_users_data_path
from app.repositories.cart_repository import CartRepository
from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.repositories.user_repository import UserRepository
from app.schemas.cart import Cart
from app.services.checkout_service import ActiveCartNotFoundError, CheckoutService, CheckoutValidationError


router = APIRouter(
    prefix="/customers/{customer_id}/checkout",
    tags=["checkout"],
    dependencies=[Depends(require_cart_owner)],
)


def get_checkout_service() -> CheckoutService:
    return CheckoutService(
        CartRepository(get_carts_data_path()),
        MenuItemRepository(get_menu_items_data_path()),
        RestaurantRepository(get_restaurants_data_path()),
        UserRepository(get_users_data_path()),
    )


@router.post(
    "/validate",
    response_model=Cart,
    responses={
        401: {"description": "Missing, invalid, or expired token, or inactive account"},
        403: {"description": "Checkout requires access to your own active customer account"},
        404: {"description": "Active cart or customer not found"},
        409: {"description": "The cart is empty or invalid, or the restaurant or an item is unavailable"},
    },
)
def validate_checkout(customer_id: CustomerId, service: CheckoutService = Depends(get_checkout_service)) -> Cart:
    """Check the active cart against current customer, restaurant, and menu data without placing an order."""
    try:
        return call(lambda: service.validate(customer_id)).cart
    except ActiveCartNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Active cart not found") from exc
    except CheckoutValidationError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
