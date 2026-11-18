from fastapi import APIRouter, Depends

from app.api.routes.cart_support import ERROR_DOCS, call, get_cart_service
from app.schemas.cart import CartView
from app.services.cart_service import CartService

router = APIRouter(prefix="/customers/{customer_id}/cart", tags=["cart"])


@router.get("", response_model=CartView, summary="Get (or create) the active cart with totals", responses=ERROR_DOCS)
def get_cart(customer_id: int, service: CartService = Depends(get_cart_service)):
    return call(lambda: service.get_cart(customer_id))
