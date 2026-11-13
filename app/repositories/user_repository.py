import json
from pathlib import Path

from app.schemas.user import UserInDB

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

    def add(self, user: UserInDB) -> UserInDB:
        users = self.get_all()
        users.append(user)

        temporary_path = self.data_path.with_suffix(".tmp")

        temporary_path.write_text(
            json.dumps(
                [item.model_dump() for item in users],
                indent=2
            ),
            encoding="utf-8"
        )

        temporary_path.replace(self.data_path)

        return user