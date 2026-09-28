"""Pydantic models (the API's data contract) for restaurants."""

from pydantic import BaseModel, Field


class Restaurant(BaseModel):
    """A restaurant as returned by the API.

    Provisional: expect to add fields (menu, hours, owner, etc.) in later milestones.
    """

    id: int = Field(..., ge=1, description="Stable unique identifier")
    name: str = Field(..., min_length=1)
    cuisine: str
    rating: float = Field(..., ge=0, le=5)
    delivery_time_minutes: int = Field(..., ge=0)
    delivery_fee: float = Field(..., ge=0)
    address: str
    is_open: bool
