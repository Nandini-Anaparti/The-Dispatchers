
from typing import Literal

from pydantic import BaseModel, Field


DeliveryStatus = Literal["pending"]


class DeliveryCreate(BaseModel):
    """Information supplied when requesting a delivery."""

    order_id: int = Field(gt=0)


class Delivery(BaseModel):
    """A delivery record created by the backend."""

    id: int = Field(gt=0)
    order_id: int = Field(gt=0)
    status: DeliveryStatus = "pending"
