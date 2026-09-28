"""Route layer: HTTP concerns only (paths, status codes, response models)."""

from fastapi import APIRouter, Depends, HTTPException

from app.core.config import get_restaurants_data_path
from app.repositories.restaurant_repository import RestaurantRepository
from app.schemas.restaurant import Restaurant
from app.services.restaurant_service import RestaurantNotFoundError, RestaurantService

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


def get_restaurant_service() -> RestaurantService:
    """Build the service with a repository pointed at the configured data file.

    FastAPI calls this for each request (via Depends), so the data path from
    config is always current. Tests can also override this dependency.
    """
    repository = RestaurantRepository(get_restaurants_data_path())
    return RestaurantService(repository)


@router.get("", response_model=list[Restaurant])
def list_restaurants(service: RestaurantService = Depends(get_restaurant_service)):
    """Return all restaurants."""
    return service.list_restaurants()


@router.get("/{restaurant_id}", response_model=Restaurant)
def get_restaurant(restaurant_id: int, service: RestaurantService = Depends(get_restaurant_service)):
    """Return one restaurant by id, or 404 if it does not exist."""
    try:
        return service.get_restaurant(restaurant_id)
    except RestaurantNotFoundError:
        raise HTTPException(status_code=404, detail=f"Restaurant {restaurant_id} not found")
