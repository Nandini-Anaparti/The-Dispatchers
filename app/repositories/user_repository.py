import json
from pathlib import Path
from threading import Lock
from app.schemas.user import UserInDB

_user_write_lock = Lock()

class UserRepository:
    def __init__(self, data_path: Path):
        self.data_path = Path(data_path)

    def get_all(self) -> list[UserInDB]:
        if not self.data_path.exists():
            raise FileNotFoundError(
                f"User data file not found: {self.data_path}"
            )

        raw = json.loads(
            self.data_path.read_text(encoding="utf-8")
        )

        if not isinstance(raw, list):
            raise ValueError("User data must be a JSON list")

        return [UserInDB(**record) for record in raw]

    def get_by_email(self, email: str) -> UserInDB | None:
        for user in self.get_all():
            if user.email.lower() == email.lower():
                return user
        return None

    def get_by_id(self, user_id: int) -> UserInDB | None:
        for user in self.get_all():
            if user.id == user_id:
                return user
        return None

    def save_all(self, users: list[UserInDB]) -> None:
        temporary_path = self.data_path.with_suffix(".tmp")

        temporary_path.write_text(
            json.dumps(
                [user.model_dump() for user in users],
                indent=2
            ),
            encoding="utf-8"
        )

        temporary_path.replace(self.data_path)

    def add(self, user: UserInDB) -> UserInDB:
        with _user_write_lock:
            users = self.get_all()
            users.append(user)
            self.save_all(users)

        return user

    def assign_restaurant(self, user_id: int, restaurant_id: int) -> None:
        with _user_write_lock:
            users = self.get_all()
            for user in users:
                if user.id == user_id:
                    if user.role != "restaurant owner":
                        raise ValueError("User is not a restaurant owner")
                    if restaurant_id not in user.restaurant_ids:
                        user.restaurant_ids.append(restaurant_id)
                    self.save_all(users)
                    return

        raise ValueError("User not found")

    def update_customer_profile(
        self, user_id: int, *, name: str, delivery_address: str | None
    ) -> UserInDB | None:
        with _user_write_lock:
            users = self.get_all()
            for user in users:
                if user.id == user_id and user.role == "customer" and user.is_active:
                    user.name = name
                    user.delivery_address = delivery_address
                    self.save_all(users)
                    return user
        return None
