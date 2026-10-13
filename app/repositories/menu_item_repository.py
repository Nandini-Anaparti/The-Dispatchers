import json
from pathlib import Path

from app.schemas.menu_item import MenuItem


class MenuItemRepository:
    def __init__(self, data_path):
        self.data_path = Path(data_path)

    def get_all(self):
        with open(self.data_path, "r") as file:
            items = json.load(file)

        result = []
        for item in items:
            result.append(MenuItem(**item))

        return result

    def get_by_restaurant(self, restaurant_id):
        items = self.get_all()
        result = []

        for item in items:
            if item.restaurant_id == restaurant_id:
                result.append(item)

        return result

    def get_by_id(self, item_id):
        items = self.get_all()

        for item in items:
            if item.id == item_id:
                return item

        return None