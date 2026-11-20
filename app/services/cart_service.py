from app.schemas.cart import Cart, CartItem, CartView
from app.services.customer_rules import require_active_customer
from app.services.pricing import price_cart


class MenuItemNotFoundError(Exception): pass
class MenuItemUnavailableError(Exception): pass
class DifferentRestaurantError(Exception): pass
class ItemNotInCartError(Exception): pass


class CartService:
    def __init__(self, cart_repo, menu_repo, restaurant_repo, user_repo):
        self.cart_repo = cart_repo
        self.menu_repo = menu_repo
        self.restaurant_repo = restaurant_repo
        self.user_repo = user_repo

    def _get_or_create(self, customer_id: int) -> Cart:
        return self.cart_repo.get_or_create_active(customer_id)

    def build_view(self, cart: Cart) -> CartView:
        """Prices always come from the CURRENT menu, never from the client."""
        menu_items = {}
        for entry in cart.items:
            item = self.menu_repo.get_by_id(entry.menu_item_id)
            if item is not None:
                menu_items[item.id] = item
        fee = 0.0
        if menu_items and cart.restaurant_id is not None:
            restaurant = self.restaurant_repo.get_by_id(cart.restaurant_id)
            fee = restaurant.delivery_fee if restaurant else 0.0
        return price_cart(cart, menu_items, fee)

    def get_cart(self, customer_id: int) -> CartView:
        require_active_customer(self.user_repo, customer_id)
        return self.build_view(self._get_or_create(customer_id))

    def add_item(self, customer_id: int, menu_item_id: int, quantity: int) -> CartView:
        require_active_customer(self.user_repo, customer_id)
        item = self.menu_repo.get_by_id(menu_item_id)
        if item is None:
            raise MenuItemNotFoundError()
        if not item.is_active or not item.is_available:
            raise MenuItemUnavailableError()

        def add(cart: Cart) -> None:
            if cart.items and cart.restaurant_id != item.restaurant_id:
                raise DifferentRestaurantError()
            cart.restaurant_id = item.restaurant_id
            existing = next((i for i in cart.items if i.menu_item_id == menu_item_id), None)
            if existing:
                existing.quantity += quantity
            else:
                cart.items.append(CartItem(menu_item_id=menu_item_id, quantity=quantity))

        cart = self.cart_repo.mutate_active(customer_id, add, create=True)
        return self.build_view(cart)

    def update_quantity(self, customer_id: int, menu_item_id: int, quantity: int) -> CartView:
        require_active_customer(self.user_repo, customer_id)

        def update(cart: Cart) -> None:
            existing = next((i for i in cart.items if i.menu_item_id == menu_item_id), None)
            if existing is None:
                raise ItemNotInCartError()
            existing.quantity = quantity

        cart = self.cart_repo.mutate_active(customer_id, update)
        if cart is None:
            raise ItemNotInCartError()
        return self.build_view(cart)

    def remove_item(self, customer_id: int, menu_item_id: int) -> CartView:
        require_active_customer(self.user_repo, customer_id)

        def remove(cart: Cart) -> None:
            remaining = [i for i in cart.items if i.menu_item_id != menu_item_id]
            if len(remaining) == len(cart.items):
                raise ItemNotInCartError()
            cart.items = remaining
            if not cart.items:
                cart.restaurant_id = None

        cart = self.cart_repo.mutate_active(customer_id, remove)
        if cart is None:
            raise ItemNotInCartError()
        return self.build_view(cart)

    def clear_cart(self, customer_id: int) -> CartView:
        require_active_customer(self.user_repo, customer_id)

        def clear(cart: Cart) -> None:
            cart.items.clear()
            cart.restaurant_id = None

        cart = self.cart_repo.mutate_active(customer_id, clear, create=True)
        return self.build_view(cart)

    