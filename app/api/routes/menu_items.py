from fastapi import APIRouter, Depends, HTTPException

from app.schemas.menu_item import MenuItem
from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.schemas.menu_item import MenuItem, MenuItemCreate, MenuItemUpdate
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

def get_menu_service():
    menu_repo = MenuItemRepository(get_menu_items_data_path())
    restaurant_repo = RestaurantRepository(get_restaurants_data_path())

    return MenuItemService(menu_repo, restaurant_repo)

@router.get("", response_model=list[MenuItem])
def get_menu_items(
    restaurant_id: int,
    service: MenuItemService = Depends(get_menu_service)
):
    """Get all menu items for a restaurant."""
    try:
        return service.get_menu_items(restaurant_id)
    except RestaurantNotFoundError:
        raise HTTPException(status_code=404, detail="Restaurant not found")

@router.get("/{item_id}", response_model=MenuItem)
def get_menu_item(
    restaurant_id: int,
    item_id: int,
    service: MenuItemService = Depends(get_menu_service)
):
    """Get a specific menu item."""
    try:
        return service.get_menu_item(restaurant_id, item_id)
    except RestaurantNotFoundError:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    except MenuItemNotFoundError:
        raise HTTPException(status_code=404, detail="Menu item not found")

    
@router.post("", response_model=MenuItem, status_code=201)
def add_menu_item(
    restaurant_id: int,
    item: MenuItemCreate,
    service: MenuItemService = Depends(get_menu_service)
):
    """Add a new menu item to a restaurant."""
    try:
        return service.add_menu_item(restaurant_id, item)
    except RestaurantNotFoundError:
        raise HTTPException(status_code=404, detail="Restaurant not found")

@router.put("/{item_id}", response_model=MenuItem)
def update_menu_item(
    restaurant_id: int,
    item_id: int,
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