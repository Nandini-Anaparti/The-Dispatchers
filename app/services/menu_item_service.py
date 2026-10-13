from app.schemas.menu_item import MenuItem

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
    
    def add_menu_item(self, restaurant_id, new_item):
        restaurant = self.restaurant_repository.get_by_id(restaurant_id)

        if restaurant is None:
            raise RestaurantNotFoundError()

        items = self.menu_repository.get_all()

        new_id = 1

        for item in items:
            if item.id >= new_id:
                new_id = item.id + 1

        menu_item = MenuItem(
            id=new_id,
            restaurant_id=restaurant_id,
            name=new_item.name,
            description=new_item.description,
            price=new_item.price,
            is_available=new_item.is_available
        )

        return self.menu_repository.add_item(menu_item)

    def update_menu_item(self, restaurant_id, item_id, updated_item):
        self.get_menu_item(restaurant_id, item_id)

        return self.menu_repository.update_item(item_id, updated_item)

class MenuItemNotFoundError(Exception):
    pass

class RestaurantNotFoundError(Exception):
    pass