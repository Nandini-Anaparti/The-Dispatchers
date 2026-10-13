class MenuItemService:
    def __init__(self, menu_repository, restaurant_repository):
        self.menu_repository = menu_repository
        self.restaurant_repository = restaurant_repository

    def get_menu_items(self, restaurant_id):
        restaurant = self.restaurant_repository.get_by_id(restaurant_id)

        if restaurant is None:
            raise RestaurantNotFoundError()

        return self.menu_repository.get_by_restaurant(restaurant_id)

    def get_menu_item(self, restaurant_id, item_id):
        restaurant = self.restaurant_repository.get_by_id(restaurant_id)

        if restaurant is None:
            raise RestaurantNotFoundError()

        item = self.menu_repository.get_by_id(item_id)

        if item is None:
            raise MenuItemNotFoundError()

        if item.restaurant_id != restaurant_id:
            raise MenuItemNotFoundError()

        return item

class MenuItemNotFoundError(Exception):
    pass

class RestaurantNotFoundError(Exception):
    pass