"""Order business rules.

CHECKOUT-03: create_order() turns a validated, re-priced cart into a saved order snapshot.
It is called AFTER checkout validation (CHECKOUT-01) and price recalculation (CHECKOUT-02),
which produce a CartView with current prices and the backend total.

CHECKOUT-04: finalize_checkout() saves the order FIRST and only then closes the cart.
If saving the order fails, the cart is left exactly as it was.
"""

from datetime import datetime, timezone

from app.schemas.cart import Cart, CartView
from app.schemas.order import Order, OrderItem


class EmptyOrderError(Exception): pass
class CartMismatchError(Exception): pass


class OrderService:
    def __init__(self, order_repo, cart_repo=None, now=None):
        self.order_repo = order_repo
        self.cart_repo = cart_repo
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

        # 1. Save the order. If this raises, we stop here and the cart is untouched.
        order = self.create_order(priced_cart)

        # 2. Only now close the cart, so the customer never loses items on a failed checkout.
        closed = cart.model_copy(update={"status": "checked_out"})
        self.cart_repo.update(closed)
        return order
