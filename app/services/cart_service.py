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

    def build_view(self, cart: Cart) -> CartView:
        """Prices always come from the CURRENT menu, never from the client."""
        lines = []
        for entry in cart.items:
            item = self.menu_repo.get_by_id(entry.menu_item_id)
            if item is None:
                continue
            lines.append(CartLine(
                menu_item_id=item.id, name=item.name, unit_price=item.price,
                quantity=entry.quantity, line_total=round(item.price * entry.quantity, 2),
            ))
        subtotal = round(sum(l.line_total for l in lines), 2)
        fee = 0.0
        if lines and cart.restaurant_id is not None:
            restaurant = self.restaurant_repo.get_by_id(cart.restaurant_id)
            fee = restaurant.delivery_fee if restaurant else 0.0
        return CartView(
            id=cart.id, customer_id=cart.customer_id, restaurant_id=cart.restaurant_id,
            status=cart.status, items=lines, subtotal=subtotal,
            delivery_fee=fee, total=round(subtotal + fee, 2),
        )

    def get_cart(self, customer_id: int) -> CartView:
        require_active_customer(self.user_repo, customer_id)
        return self.build_view(self._get_or_create(customer_id))

    def add_item(self, customer_id: int, menu_item_id: int, quantity: int) -> CartView:
        require_active_customer(self.user_repo, customer_id)
        cart = self._get_or_create(customer_id)
        item = self.menu_repo.get_by_id(menu_item_id)
        if item is None:
            raise MenuItemNotFoundError()
        if not item.is_available:
            raise MenuItemUnavailableError()
        if cart.items and cart.restaurant_id != item.restaurant_id:
            raise DifferentRestaurantError()

        cart.restaurant_id = item.restaurant_id
        existing = next((i for i in cart.items if i.menu_item_id == menu_item_id), None)
        if existing:
            existing.quantity += quantity
        else:
            cart.items.append(CartItem(menu_item_id=menu_item_id, quantity=quantity))
        self.cart_repo.update(cart)
        return self.build_view(cart)

    def update_quantity(self, customer_id: int, menu_item_id: int, quantity: int) -> CartView:
        require_active_customer(self.user_repo, customer_id)
        cart = self._get_or_create(customer_id)
        existing = next((i for i in cart.items if i.menu_item_id == menu_item_id), None)
        if existing is None:
            raise ItemNotInCartError()
        existing.quantity = quantity
        self.cart_repo.update(cart)
        return self.build_view(cart)

    def remove_item(self, customer_id: int, menu_item_id: int) -> CartView:
        require_active_customer(self.user_repo, customer_id)
        cart = self._get_or_create(customer_id)
        if not any(i.menu_item_id == menu_item_id for i in cart.items):
            raise ItemNotInCartError()
        cart.items = [i for i in cart.items if i.menu_item_id != menu_item_id]
        if not cart.items:
            cart.restaurant_id = None
        self.cart_repo.update(cart)
        return self.build_view(cart)

