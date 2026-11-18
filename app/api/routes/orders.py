"""HTTP layer for ORDER-01: customers retrieve their own orders."""

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_current_user
from app.core.config import get_users_data_path
from app.core.order_config import get_orders_data_path
from app.repositories.order_repository import OrderRepository
from app.repositories.user_repository import UserRepository
from app.schemas.order import Order
from app.schemas.user import UserInDB
from app.services.customer_rules import CustomerInactiveError, CustomerNotFoundError
from app.services.order_service import OrderNotFoundError, OrderService


def require_order_owner(
    customer_id: int, current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    if current_user.role != "customer" or current_user.id != customer_id:
        raise HTTPException(status_code=403, detail="You can only view your own orders")
    return current_user


router = APIRouter(
    prefix="/customers/{customer_id}/orders",
    tags=["orders"],
    dependencies=[Depends(require_order_owner)],
)

ERRORS = {
    CustomerNotFoundError: (404, "Customer not found"),
    CustomerInactiveError: (403, "Customer account is deactivated"),
    OrderNotFoundError: (404, "Order not found"),
}

RESPONSES = {
    401: {"description": "Missing or invalid authentication"},
    403: {"description": "You can only view your own orders"},
    404: {"description": "Customer or order not found"},
}


def get_order_service() -> OrderService:
    return OrderService(
        OrderRepository(get_orders_data_path()),
        user_repo=UserRepository(get_users_data_path()),
    )


def call(action):
    try:
        return action()
    except tuple(ERRORS) as exc:
        status, detail = ERRORS[type(exc)]
        raise HTTPException(status_code=status, detail=detail) from exc


@router.get("", response_model=list[Order], responses=RESPONSES,
            summary="Your order history (newest first)")
def list_orders(customer_id: int, service: OrderService = Depends(get_order_service)):
    return call(lambda: service.list_orders(customer_id))


@router.get("/{order_id}", response_model=Order, responses=RESPONSES,
            summary="One of your orders")
def get_order(customer_id: int, order_id: int, service: OrderService = Depends(get_order_service)):
    return call(lambda: service.get_order(customer_id, order_id))
