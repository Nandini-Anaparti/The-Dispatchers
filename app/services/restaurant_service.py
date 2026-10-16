"""Service layer: application/business logic for restaurants.

Routes call the service; the service calls the repository. The service never
touches files directly and never deals with HTTP details.
"""

from app.repositories.restaurant_repository import RestaurantRepository
from app.schemas.restaurant import Restaurant


class RestaurantNotFoundError(Exception):
    """Raised when a requested restaurant does not exist."""


class RestaurantService:
    def __init__(self, repository: RestaurantRepository):
        self.repository = repository

    def list_restaurants(
        self,
        name: str | None = None,
        cuisine: str | None = None,
        is_open: bool | None = None,
        min_rating: float | None = None,
    ) -> list[Restaurant]:
        """Return restaurants, optionally narrowed down by filters.

        Every filter is optional. A restaurant is kept only if it passes all
        the filters that were given.
        - name: case-insensitive partial match ("piz" matches "La Vela Pizzeria")
        - cuisine: case-insensitive exact match ("italian" matches "Italian")
        - is_open: only open (True) or only closed (False) restaurants
        - min_rating: only restaurants rated at least this high
        """
        results = []
        for restaurant in self.repository.get_all():
            if name is not None and name.lower() not in restaurant.name.lower():
                continue
            if cuisine is not None and cuisine.lower() != restaurant.cuisine.lower():
                continue
            if is_open is not None and restaurant.is_open != is_open:
                continue
            if min_rating is not None and restaurant.rating < min_rating:
                continue
            results.append(restaurant)
        return results

    def get_restaurant(self, restaurant_id: int) -> Restaurant:
        restaurant = self.repository.get_by_id(restaurant_id)
        if restaurant is None:
            raise RestaurantNotFoundError(f"Restaurant {restaurant_id} not found")
        return restaurant
