"""Order business rules.

CHECKOUT-03: create_order() turns a validated, re-priced cart into a saved order snapshot.
It is called AFTER checkout validation (CHECKOUT-01) and price recalculation (CHECKOUT-02),
which produce a CartView with current prices and the backend total.

CHECKOUT-04: finalize_checkout() saves the order FIRST and only then closes the cart.
If saving the order fails, the cart is left exactly as it was.

ORDER-01: get_order() and list_orders() let a customer see their own orders.
"""

from datetime import datetime, timezone

from app.core.config import get_users_data_path
from app.repositories.user_repository import UserRepository
from app.schemas.cart import Cart, CartView
from app.schemas.order import Order, OrderItem
from app.services.customer_rules import require_active_customer


class EmptyOrderError(Exception): pass
class CartMismatchError(Exception): pass
class OrderNotFoundError(Exception): pass


class OrderService:
    def __init__(self, order_repo, cart_repo=None, now=None, *, user_repo=None):
        self.order_repo = order_repo
        self.cart_repo = cart_repo
        self.user_repo = user_repo
        self.now = now or (lambda: datetime.now(timezone.utc))

    def create_order(self, priced_cart: CartView) -> Order:
        if not priced_cart.items or priced_cart.restaurant_id is None:
            raise EmptyOrderError()

        items = [
            OrderItem(
                menu_item_id=line.menu_item_id, name=line.name, unit_price=line.unit_price,
                quantity=line.quantity, line_total=line.line_total,
            )
            for line in priced_cart.items
        ]
        return self.order_repo.add(
            customer_id=priced_cart.customer_id,
            restaurant_id=priced_cart.restaurant_id,
            items=items,
            subtotal=priced_cart.subtotal,
            delivery_fee=priced_cart.delivery_fee,
            total=priced_cart.total,
            status="placed",
            created_at=self.now(),
        )

    def finalize_checkout(self, cart: Cart, priced_cart: CartView) -> Order:
        if cart.id != priced_cart.id or cart.customer_id != priced_cart.customer_id:
            raise CartMismatchError()

        user_repo = self.user_repo if self.user_repo is not None else UserRepository(get_users_data_path())
        require_active_customer(user_repo, cart.customer_id)

        # 1. Save the order. If this raises, we stop here and the cart is untouched.
        order = self.create_order(priced_cart)

        # 2. Only now close the cart, so the customer never loses items on a failed checkout.
        closed = cart.model_copy(update={"status": "checked_out"})
        self.cart_repo.update(closed)
        return order

    def list_orders(self, customer_id: int) -> list[Order]:
        require_active_customer(self.user_repo, customer_id)
        orders = self.order_repo.get_by_customer(customer_id)
        return sorted(orders, key=lambda o: (o.created_at, o.id), reverse=True)  # newest first

    def get_order(self, customer_id: int, order_id: int) -> Order:
        require_active_customer(self.user_repo, customer_id)
        order = self.order_repo.get_by_id(order_id)
        # Another customer's order looks "not found", so IDs can't be probed.
        if order is None or order.customer_id != customer_id:
            raise OrderNotFoundError()
        return order
