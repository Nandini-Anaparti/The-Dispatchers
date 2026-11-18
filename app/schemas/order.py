"""Pydantic models for orders.

An order is a snapshot: it copies the item names and prices at checkout time,
so later menu changes never change an old order.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

OrderStatus = Literal["placed", "preparing", "ready", "delivered", "completed", "cancelled"]


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
