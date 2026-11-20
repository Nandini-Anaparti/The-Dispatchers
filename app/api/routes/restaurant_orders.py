"""HTTP layer for ORDER-02: restaurant staff view and progress their restaurant's orders.

Access: the restaurant's owner or an admin (require_restaurant_access).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path

from app.core.order_config import get_orders_data_path
from app.core.permissions import require_restaurant_access
from app.repositories.order_repository import OrderRepository
from app.schemas.order import Order, OrderStatusUpdate
from app.services.order_service import (
    InvalidStatusTransitionError, OrderNotFoundError, OrderService,
)

RestaurantId = Annotated[int, Path(description="ID of the restaurant whose orders are being managed")]
OrderId = Annotated[int, Path(description="ID of a saved order placed at this restaurant")]

router = APIRouter(
    prefix="/restaurants/{restaurant_id}/orders",
    tags=["restaurant orders"],
    dependencies=[Depends(require_restaurant_access)],
)

RESPONSES = {
    401: {"description": "Missing or invalid authentication"},
    403: {"description": "Only this restaurant's owner or an admin can manage its orders"},
}


def get_order_service() -> OrderService:
    return OrderService(OrderRepository(get_orders_data_path()))


@router.get("", response_model=list[Order], responses=RESPONSES,
            summary="List this restaurant's orders (newest first)")
def list_restaurant_orders(restaurant_id: RestaurantId,
                           service: OrderService = Depends(get_order_service)):
    """Return every order placed at this restaurant, newest first, for its owner or an admin."""
    return service.list_restaurant_orders(restaurant_id)


@router.patch("/{order_id}/status", response_model=Order,
              responses={**RESPONSES,
                         404: {"description": "Order not found for this restaurant"},
                         409: {"description": "That status change is not allowed"}},
              summary="Move an order to its next status")
def update_order_status(restaurant_id: RestaurantId, order_id: OrderId, data: OrderStatusUpdate,
                        service: OrderService = Depends(get_order_service)):
    """Move the order to the requested status. Only allowed moves succeed
    (placed -> preparing -> ready -> delivered -> completed, or cancelled from placed or preparing);
    anything else returns 409 and the order is left unchanged."""
    try:
        return service.update_status(restaurant_id, order_id, data.status)
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Order not found") from exc
    except InvalidStatusTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
