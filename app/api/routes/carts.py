from fastapi import APIRouter, Depends

from app.api.routes.cart_support import ERROR_DOCS, call, get_cart_service
from app.schemas.cart import CartItemAdd, CartItemUpdate, CartView
from app.services.cart_service import CartService

router = APIRouter(prefix="/customers/{customer_id}/cart", tags=["cart"])


@router.get("", response_model=CartView, summary="Get (or create) the active cart with totals", responses=ERROR_DOCS)
def get_cart(customer_id: int, service: CartService = Depends(get_cart_service)):
    return call(lambda: service.get_cart(customer_id))


@router.post("/items", response_model=CartView, summary="Add an item to the cart", responses=ERROR_DOCS)
def add_item(customer_id: int, body: CartItemAdd, service: CartService = Depends(get_cart_service)):
    return call(lambda: service.add_item(customer_id, body.menu_item_id, body.quantity))


@router.put("/items/{menu_item_id}", response_model=CartView,
            summary="Change an item's quantity", responses=ERROR_DOCS)
def update_item(customer_id: int, menu_item_id: int, body: CartItemUpdate,
                service: CartService = Depends(get_cart_service)):
    return call(lambda: service.update_quantity(customer_id, menu_item_id, body.quantity))

