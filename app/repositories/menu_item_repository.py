from pathlib import Path
from threading import RLock

from app.repositories.json_storage import read_json_list, write_json_list_atomic
from app.schemas.menu_item import MenuItem

# One lock for every MenuItemRepository, so two requests that change the menu at
# the same time cannot both read the old list and overwrite each other's change.
_menu_lock = RLock()


class MenuItemRepository:
    def __init__(self, data_path):
        self.data_path = Path(data_path)

    def get_all(self):
        with _menu_lock:
            return [MenuItem(**item) for item in read_json_list(self.data_path)]

    def get_by_restaurant(self, restaurant_id):
        return [item for item in self.get_all() if item.restaurant_id == restaurant_id]

    def get_by_id(self, item_id):
        return next((item for item in self.get_all() if item.id == item_id), None)

    def save_all(self, items):
        with _menu_lock:
            write_json_list_atomic(self.data_path, [item.model_dump() for item in items])

    def add_item(self, item):
        with _menu_lock:  # read, change and save as one step
            items = self.get_all()
            items.append(item)
            self.save_all(items)
        return item

    def update_item(self, item_id, updated_item):
        with _menu_lock:
            items = self.get_all()
            for item in items:
                if item.id == item_id:
                    item.name = updated_item.name
                    item.description = updated_item.description
                    item.price = updated_item.price
                    item.is_available = updated_item.is_available
                    self.save_all(items)
                    return item
        return None

    def deactivate_item(self, item_id):
        with _menu_lock:
            items = self.get_all()
            for item in items:
                if item.id == item_id:
                    item.is_active = False
                    item.is_available = False
                    self.save_all(items)
                    return item
        return None
