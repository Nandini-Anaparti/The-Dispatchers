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


class RestaurantCreate(BaseModel):
    """What a restaurant manager sends to create a restaurant.

    No id here: the server picks the next free id.
    """

    name: str = Field(..., min_length=1)
    cuisine: str = Field(..., min_length=1)
    rating: float = Field(0, ge=0, le=5)
    delivery_time_minutes: int = Field(..., ge=0)
    delivery_fee: float = Field(..., ge=0)
    address: str = Field(..., min_length=1)
    is_open: bool = True


class RestaurantUpdate(BaseModel):
    """What a restaurant manager sends to update a restaurant.

    Every field is optional, so you only send what you want to change.
    """

    name: str | None = Field(None, min_length=1)
    cuisine: str | None = Field(None, min_length=1)
    rating: float | None = Field(None, ge=0, le=5)
    delivery_time_minutes: int | None = Field(None, ge=0)
    delivery_fee: float | None = Field(None, ge=0)
    address: str | None = Field(None, min_length=1)
    is_open: bool | None = None
