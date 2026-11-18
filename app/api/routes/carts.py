from fastapi import APIRouter, Depends

from app.api.routes.cart_support import ERROR_DOCS, call, get_cart_service, require_cart_owner
from app.schemas.cart import Cart
from app.services.cart_service import CartService

router = APIRouter(prefix="/customers/{customer_id}/cart", tags=["cart"])


@router.get(
    "",
    response_model=Cart,
    summary="Get (or create) your active cart",
    responses={status: ERROR_DOCS[status] for status in (401, 403, 404)},
    dependencies=[Depends(require_cart_owner)],
)
def get_cart(customer_id: int, service: CartService = Depends(get_cart_service)):
    return call(lambda: service.get_cart(customer_id))

