from typing import Literal
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError
from app.schemas.user import (
    AccountRegister,
    CustomerRegister,
    CustomerProfile,
    CustomerProfileUpdate,
    RestaurantOwnerRegister,
    User,
    UserInDB
)
from app.repositories.user_repository import UserRepository

class EmailAlreadyRegisteredError(Exception):
    pass

class CustomerProfileUnavailableError(Exception):
    pass

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
        self.password_hasher = PasswordHasher()

    def register_customer(self, data: CustomerRegister) -> User:
        return self._register_user(data, "customer", data.delivery_address)

    def update_customer_profile(self, customer_id: int, data: CustomerProfileUpdate) -> CustomerProfile:
        user = self.repository.update_customer_profile(customer_id, data)
        if user is None:
            raise CustomerProfileUnavailableError()
        return CustomerProfile.model_validate(user, from_attributes=True)

    def register_restaurant_owner(self, data: RestaurantOwnerRegister) -> User:
        return self._register_user(data, "restaurant owner")

    def _register_user(
        self,
        data: AccountRegister,
        role: Literal["customer", "restaurant owner"],
        delivery_address: str | None = None
    ) -> User:
        email = str(data.email).lower()

        if self.repository.get_by_email(email) is not None:
            raise EmailAlreadyRegisteredError()

        users = self.repository.get_all()
        next_id = max((user.id for user in users), default=0) + 1

        new_user = UserInDB(
            id=next_id,
            name=data.name,
            email=email,
            password_hash=self.password_hasher.hash(data.password),
            role=role,
            is_active=True,
            delivery_address=delivery_address,
            restaurant_ids=[]
        )

        self.repository.add(new_user)

        return User(
            id=new_user.id,
            name=new_user.name,
            email=new_user.email,
            role=new_user.role,
            is_active=new_user.is_active,
            delivery_address=new_user.delivery_address
        )

    def authenticate_user(self, email: str, password: str) -> UserInDB | None:

        user = self.repository.get_by_email(email)

        if user is None or not user.is_active:
            return None

        try:
            self.password_hasher.verify(
                user.password_hash,
                password
            )
        except (VerificationError, InvalidHashError):
            return None

        return user
