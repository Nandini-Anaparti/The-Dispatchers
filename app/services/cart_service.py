from app.schemas.cart import Cart, CartItem, CartLine, CartView
from app.services.customer_rules import require_active_customer


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
        cart = self.cart_repo.get_active_by_customer(customer_id)
        if cart is None:
            next_id = max((c.id for c in self.cart_repo.get_all()), default=0) + 1
            cart = self.cart_repo.add(Cart(id=next_id, customer_id=customer_id))
        return cart

    def get_cart(self, customer_id: int) -> Cart:
        require_active_customer(self.user_repo, customer_id)
        return self._get_or_create(customer_id)