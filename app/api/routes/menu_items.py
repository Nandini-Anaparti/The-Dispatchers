from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.schemas.menu_item import MenuItem, MenuItemCreate, MenuItemUpdate
from app.core.permissions import RestaurantId, require_restaurant_access
from app.services.menu_item_service import (
    MenuItemService,
    MenuItemNotFoundError,
    RestaurantNotFoundError
)
from app.core.config import (
    get_menu_items_data_path,
    get_restaurants_data_path
)

router = APIRouter(
    prefix="/restaurants/{restaurant_id}/menu-items",
    tags=["menu-items"]
)
MenuItemId = Annotated[int, Path(description="ID of the menu item within the restaurant")]
RESTAURANT_NOT_FOUND = {404: {"description": "Restaurant not found"}}
ITEM_NOT_FOUND = {404: {"description": "Restaurant or active menu item not found in this restaurant"}}
MANAGEMENT_ERRORS = {
    401: {"description": "Missing, invalid, or expired token, or inactive account"},
    403: {"description": "Permission to manage this restaurant is required"},
}

def get_menu_service():
    menu_repo = MenuItemRepository(get_menu_items_data_path())
    restaurant_repo = RestaurantRepository(get_restaurants_data_path())

    return MenuItemService(menu_repo, restaurant_repo)


@router.get("", response_model=list[MenuItem], responses=RESTAURANT_NOT_FOUND)
def get_menu_items(
    restaurant_id: RestaurantId,
    name: Annotated[str | None, Query(description="Case-insensitive partial item name")] = None,
    max_price: Annotated[float | None, Query(description="Maximum item price, inclusive and nonnegative")] = None,
    is_available: Annotated[bool | None, Query(description="Filter by current item availability")] = None,
    service: MenuItemService = Depends(get_menu_service)
):
    """List active menu items publicly. A negative maximum price returns 422."""
    if max_price is not None and max_price < 0:
        raise HTTPException(
            status_code=422,
            detail="Maximum price cannot be negative"
        )

    try:
        return service.get_menu_items(
            restaurant_id,
            name,
            max_price,
            is_available
        )
    except RestaurantNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found"
        )

@router.get(
    "/manage",
    response_model=list[MenuItem],
    dependencies=[Depends(require_restaurant_access)],
    responses={**MANAGEMENT_ERRORS, **RESTAURANT_NOT_FOUND},
)
def get_managed_menu_items(
    restaurant_id: RestaurantId,
    service: MenuItemService = Depends(get_menu_service)
):
    """List a managed restaurant's menu items, including deactivated items."""
    try:
        return service.get_menu_items(
            restaurant_id,
            include_inactive=True
        )

    except RestaurantNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found"
        )

@router.get("/{item_id}", response_model=MenuItem, responses=ITEM_NOT_FOUND)
def get_menu_item(
    restaurant_id: RestaurantId,
    item_id: MenuItemId,
    service: MenuItemService = Depends(get_menu_service)
):
    """Return an active menu item for the specified restaurant."""
    try:
        return service.get_menu_item(restaurant_id, item_id)
    except RestaurantNotFoundError:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    except MenuItemNotFoundError:
        raise HTTPException(status_code=404, detail="Menu item not found")

    
@router.post(
    "",
    response_model=MenuItem,
    status_code=201,
    dependencies=[Depends(require_restaurant_access)],
    responses={**MANAGEMENT_ERRORS, **RESTAURANT_NOT_FOUND},
)
def add_menu_item(
    restaurant_id: RestaurantId,
    item: MenuItemCreate,
    service: MenuItemService = Depends(get_menu_service)
):
    """Add a new menu item to a restaurant."""
    try:
        return service.add_menu_item(restaurant_id, item)
    except RestaurantNotFoundError:
        raise HTTPException(status_code=404, detail="Restaurant not found")

@router.put(
    "/{item_id}",
    response_model=MenuItem,
    dependencies=[Depends(require_restaurant_access)],
    responses={**MANAGEMENT_ERRORS, **ITEM_NOT_FOUND},
)
def update_menu_item(
    restaurant_id: RestaurantId,
    item_id: MenuItemId,
    item: MenuItemUpdate,
    service: MenuItemService = Depends(get_menu_service)
):
    """Update an existing menu item."""
    try:
        return service.update_menu_item(restaurant_id, item_id, item)
    except RestaurantNotFoundError:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    except MenuItemNotFoundError:
        raise HTTPException(status_code=404, detail="Menu item not found")

@router.patch(
    "/{item_id}/deactivate",
    response_model=MenuItem,
    dependencies=[Depends(require_restaurant_access)],
    responses={**MANAGEMENT_ERRORS, **ITEM_NOT_FOUND},
)
def deactivate_menu_item(
    restaurant_id: RestaurantId,
    item_id: MenuItemId,
    service: MenuItemService = Depends(get_menu_service)
):
    """Mark an active menu item inactive and unavailable."""
    try:
        return service.deactivate_menu_item(restaurant_id, item_id)

    except RestaurantNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found"
        )

    except MenuItemNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Menu item not found"
        )
