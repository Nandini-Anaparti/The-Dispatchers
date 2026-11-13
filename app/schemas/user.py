from typing import Literal
from pydantic import BaseModel, EmailStr, Field, field_validator

class CustomerRegister(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=8)
    delivery_address: str | None = None

    @field_validator("name")
    @classmethod
    def name_cannot_be_blank(cls, name):
        name = name.strip()
        if not name:
            raise ValueError("Name cannot be blank")
        return name

class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: Literal["customer", "restaurant owner", "admin"]
    is_active: bool = True
    delivery_address: str | None = None

class UserInDB(User):
    password_hash: str