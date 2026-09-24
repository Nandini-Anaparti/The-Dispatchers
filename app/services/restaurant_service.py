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

    def list_restaurants(self) -> list[Restaurant]:
        return self.repository.get_all()

    def get_restaurant(self, restaurant_id: int) -> Restaurant:
        restaurant = self.repository.get_by_id(restaurant_id)
        if restaurant is None:
            raise RestaurantNotFoundError(f"Restaurant {restaurant_id} not found")
        return restaurant
