from typing import Literal
from pydantic import BaseModel, Field


class CartItem(BaseModel):
    menu_item_id: int
    quantity: int = Field(ge=1, strict=True)


class Cart(BaseModel):
    id: int
    customer_id: int
    restaurant_id: int | None = None
    status: Literal["active", "checked_out"] = "active"
    items: list[CartItem] = []


class CartItemAdd(BaseModel):
    menu_item_id: int
    quantity: int = Field(1, ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)


class CartLine(BaseModel):
    menu_item_id: int
    name: str
    unit_price: float
    quantity: int
    line_total: float


class CartView(BaseModel):
    id: int
    customer_id: int
    restaurant_id: int | None
    status: str
    items: list[CartLine]
    subtotal: float
    delivery_fee: float
    total: float
