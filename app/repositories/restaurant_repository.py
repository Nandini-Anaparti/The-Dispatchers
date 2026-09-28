"""Repository layer: the only place that reads restaurant data from storage."""

import json
from pathlib import Path

from app.schemas.restaurant import Restaurant


class RestaurantRepository:
    """Loads restaurants from a JSON file.

    The file path is passed in (not hard-coded) so the app and the tests can
    use different data files.
    """

    def __init__(self, data_path: Path):
        self.data_path = Path(data_path)

    def get_all(self) -> list[Restaurant]:
        """Return every restaurant in the data file.

        Raises:
            FileNotFoundError: the data file does not exist.
            ValueError: the file is not valid JSON, is not a list, or a
                record does not match the Restaurant model.
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"Restaurant data file not found: {self.data_path}")

        try:
            raw = json.loads(self.data_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Restaurant data file is not valid JSON: {self.data_path}") from exc

        if not isinstance(raw, list):
            raise ValueError("Restaurant data must be a JSON list")

        # Pydantic's ValidationError is a subclass of ValueError,
        # so bad records also surface as ValueError.
        return [Restaurant(**record) for record in raw]

    def get_by_id(self, restaurant_id: int) -> Restaurant | None:
        """Return the restaurant with this id, or None if there isn't one."""
        for restaurant in self.get_all():
            if restaurant.id == restaurant_id:
                return restaurant
        return None
