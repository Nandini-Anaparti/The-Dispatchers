"""Place an order from the customer's active cart.

This connects the whole checkout chain in one place:
  1. CheckoutService.validate()  -> customer, cart, restaurant and menu items are still valid (CHECKOUT-01)
  2. CheckoutService.price()     -> prices and total recalculated from the CURRENT menu (CHECKOUT-02)
  3. OrderService.finalize_checkout() -> order saved first, cart closed only after (CHECKOUT-03/04)

Nothing is written until steps 1 and 2 pass, so a failed checkout never leaves a half-made order.
"""

from app.schemas.order import Order


class PlaceOrderService:
    def __init__(self, checkout_service, order_service):
        self.checkout_service = checkout_service
        self.order_service = order_service

    def place_order(self, customer_id: int) -> Order:
        validated = self.checkout_service.validate(customer_id)
        priced_cart = self.checkout_service.price(validated)
        return self.order_service.finalize_checkout(validated.cart, priced_cart)
