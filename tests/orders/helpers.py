"""Small helpers shared by the order lifecycle tests."""

from datetime import datetime, timedelta, timezone

from app.core.auth import create_access_token
from app.services.order_service import OrderService


def auth(user_id):
    return {"Authorization": f"Bearer {create_access_token(user_id)}"}


def place_orders(order_env, priced_cart, customer_id=1, count=1):
    """Create orders through CHECKOUT-03 with a clock that moves 1 minute each time."""
    ticks = iter(datetime(2026, 11, 18, tzinfo=timezone.utc) + timedelta(minutes=i) for i in range(20))
    service = OrderService(order_env.order_repo, now=lambda: next(ticks))
    cart = priced_cart.model_copy(update={"customer_id": customer_id})
    return [service.create_order(cart) for _ in range(count)]


def move_to(service, order, *statuses):
    """Walk an order through several statuses using the real transition rules."""
    for status in statuses:
        order = service.update_status(order.restaurant_id, order.id, status)
    return order
