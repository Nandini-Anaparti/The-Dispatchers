from pydantic import BaseModel, Field


class MenuItem(BaseModel):
    id: int
    restaurant_id: int
    name: str
    description: str
    price: float = Field(gt=0)
    is_available: bool