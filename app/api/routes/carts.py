from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.api.routes.cart_support import CustomerId, ERROR_DOCS, call, get_cart_service, require_cart_owner
from app.schemas.cart import CartItemAdd, CartItemUpdate, CartView
from app.services.cart_service import CartService

CartItemId = Annotated[int, Path(description="Menu item ID of the line in the cart")]
ACCESS_ERRORS = {status: ERROR_DOCS[status] for status in (401, 403, 404)}

router = APIRouter(
    prefix="/customers/{customer_id}/cart",
    tags=["cart"],
    dependencies=[Depends(require_cart_owner)],
)


@router.get("", response_model=CartView, summary="Get (or create) the active cart with totals", responses=ACCESS_ERRORS)
def get_cart(customer_id: CustomerId, service: CartService = Depends(get_cart_service)):
    """Return the customer's active cart, creating an empty cart if needed. Totals use current menu prices."""
    return call(lambda: service.get_cart(customer_id))


@router.post("/items", response_model=CartView, summary="Add an item to the cart", responses=ERROR_DOCS)
def add_item(customer_id: CustomerId, body: CartItemAdd, service: CartService = Depends(get_cart_service)):
    """Add an active, available menu item. The quantity is added to any existing line for the item."""
    return call(lambda: service.add_item(customer_id, body.menu_item_id, body.quantity))


@router.put("/items/{menu_item_id}", response_model=CartView,
            summary="Change an item's quantity", responses=ACCESS_ERRORS)
def update_item(customer_id: CustomerId, menu_item_id: CartItemId, body: CartItemUpdate,
                service: CartService = Depends(get_cart_service)):
    """Replace the quantity of an existing cart line and return recalculated totals."""
    return call(lambda: service.update_quantity(customer_id, menu_item_id, body.quantity))


@router.delete("/items/{menu_item_id}", response_model=CartView,
               summary="Remove an item from the cart", responses=ACCESS_ERRORS)
def remove_item(customer_id: CustomerId, menu_item_id: CartItemId, service: CartService = Depends(get_cart_service)):
    """Remove the entire line for the given menu item and return recalculated totals."""
    return call(lambda: service.remove_item(customer_id, menu_item_id))


@router.delete("", response_model=CartView, summary="Clear the cart", responses=ACCESS_ERRORS)
def clear_cart(customer_id: CustomerId, service: CartService = Depends(get_cart_service)):
    """Empty the active cart, or create an empty cart if needed, and return zero totals."""
    return call(lambda: service.clear_cart(customer_id))
