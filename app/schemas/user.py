from typing import Literal
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

class AccountRegister(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("name")
    @classmethod
    def name_cannot_be_blank(cls, name):
        name = name.strip()

        if not name:
            raise ValueError("Name cannot be blank")

        return name

class CustomerRegister(AccountRegister):
    delivery_address: str | None = None

class RestaurantOwnerRegister(AccountRegister):
    model_config = ConfigDict(extra="forbid")

class DeliveryAddress(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    street: str = Field(min_length=1)
    city: str = Field(min_length=1)
    region: str = Field(min_length=1)
    postal_code: str = Field(min_length=1)
    country: str = Field(min_length=1)

    def formatted(self) -> str:
        return f"{self.street}, {self.city}, {self.region} {self.postal_code}, {self.country}"


class CustomerProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1)
    delivery_address: DeliveryAddress | str | None = None

    @field_validator("delivery_address")
    @classmethod
    def legacy_address_cannot_be_blank(cls, address):
        if address == "":
            raise ValueError("Delivery address cannot be blank")
        return address

class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: Literal["customer", "restaurant owner", "admin"]
    is_active: bool = True
    delivery_address: str | None = None

class CustomerProfile(User):
    delivery_address_details: DeliveryAddress | None = None


class UserInDB(CustomerProfile):
    password_hash: str
    restaurant_ids: list[int] = Field(default_factory=list)
