from argon2 import PasswordHasher

from app.schemas.user import CustomerRegister, User, UserInDB
from app.repositories.user_repository import UserRepository

class EmailAlreadyRegisteredError(Exception):
    pass

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
        self.password_hasher = PasswordHasher()

    def register_customer(self, data: CustomerRegister) -> User:
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
            role="customer",
            is_active=True,
            delivery_address=data.delivery_address
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