"""Pydantic models for orders.

An order is a snapshot: it copies the item names and prices at checkout time,
so later menu changes never change an old order.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

OrderStatus = Literal["placed", "preparing", "ready", "delivered", "completed", "cancelled"]

# ORDER-02: the only allowed status moves. Completed and cancelled are final.
# (Team-agreed rule: the M2 instructions do not prescribe specific transitions.)
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "placed": {"preparing", "cancelled"},
    "preparing": {"ready", "cancelled"},
    "ready": {"delivered"},
    "delivered": {"completed"},
    "completed": set(),
    "cancelled": set(),
}


class OrderItem(BaseModel):
    menu_item_id: int
    name: str
    unit_price: float = Field(ge=0)   # price at checkout time
    quantity: int = Field(ge=1)
    line_total: float = Field(ge=0)


class Order(BaseModel):
    id: int
    customer_id: int
    restaurant_id: int
    items: list[OrderItem] = Field(min_length=1)
    subtotal: float = Field(ge=0)
    delivery_fee: float = Field(ge=0)
    total: float = Field(ge=0)
    status: OrderStatus = "placed"
    created_at: datetime


class OrderStatusUpdate(BaseModel):
    """What restaurant staff send to move an order to its next status."""

    status: OrderStatus
