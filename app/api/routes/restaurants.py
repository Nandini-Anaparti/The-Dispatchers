"""Route layer: HTTP concerns only (paths, status codes, response models)."""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.config import get_restaurants_data_path
from app.repositories.restaurant_repository import RestaurantRepository
from app.schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate
from app.services.restaurant_service import RestaurantNotFoundError, RestaurantService

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

# Shared description of the 404 error so it shows up in the OpenAPI docs.
NOT_FOUND_RESPONSE = {
    404: {
        "description": "No restaurant exists with this id",
        "content": {"application/json": {"example": {"detail": "Restaurant 999 not found"}}},
    }
}


def get_restaurant_service() -> RestaurantService:
    """Build the service with a repository pointed at the configured data file.

    FastAPI calls this for each request (via Depends), so the data path from
    config is always current. Tests can also override this dependency.
    """
    repository = RestaurantRepository(get_restaurants_data_path())
    return RestaurantService(repository)


@router.get("", response_model=list[Restaurant], summary="List, search, and filter restaurants")
def list_restaurants(
    name: str | None = Query(None, description="Part of the restaurant name (case-insensitive)"),
    cuisine: str | None = Query(None, description="Exact cuisine, e.g. Italian (case-insensitive)"),
    is_open: bool | None = Query(None, description="true = only open, false = only closed"),
    min_rating: float | None = Query(None, ge=0, le=5, description="Minimum rating from 0 to 5"),
    service: RestaurantService = Depends(get_restaurant_service),
):
    """Return all restaurants, or only the ones matching the optional filters.

    With no query parameters this returns every restaurant.
    A min_rating outside 0 to 5 returns 422.
    """
    return service.list_restaurants(name=name, cuisine=cuisine, is_open=is_open, min_rating=min_rating)


@router.get(
    "/{restaurant_id}",
    response_model=Restaurant,
    summary="Get one restaurant",
    responses=NOT_FOUND_RESPONSE,
)
def get_restaurant(restaurant_id: int, service: RestaurantService = Depends(get_restaurant_service)):
    """Return one restaurant by id, or 404 if it does not exist."""
    try:
        return service.get_restaurant(restaurant_id)
    except RestaurantNotFoundError:
        raise HTTPException(status_code=404, detail=f"Restaurant {restaurant_id} not found")



@router.post("", response_model=Restaurant, status_code=201, summary="Create a restaurant")
def create_restaurant(data: RestaurantCreate, service: RestaurantService = Depends(get_restaurant_service)):
    """Create a new restaurant. The server assigns the id.

    Returns 201 with the created restaurant, or 422 if the body is invalid.
    """
    return service.create_restaurant(data)


@router.put(
    "/{restaurant_id}",
    response_model=Restaurant,
    summary="Update a restaurant",
    responses=NOT_FOUND_RESPONSE,
)
def update_restaurant(
    restaurant_id: int,
    changes: RestaurantUpdate,
    service: RestaurantService = Depends(get_restaurant_service),
):
    """Update a restaurant. Only the fields you send are changed.

    Returns 404 if the restaurant does not exist, or 422 if a field is invalid.
    """
    try:
        return service.update_restaurant(restaurant_id, changes)
    except RestaurantNotFoundError:
        raise HTTPException(status_code=404, detail=f"Restaurant {restaurant_id} not found")
