"""One place that turns a cart into prices.

The cart view (CART-06) and checkout (CHECKOUT-02) need the same numbers, so the
calculation lives here instead of being copied into each service.
"""

from app.schemas.cart import Cart, CartLine, CartView
from app.schemas.menu_item import MenuItem


def price_cart(cart: Cart, menu_items: dict[int, MenuItem], delivery_fee: float) -> CartView:
    """Price a cart from the CURRENT menu items passed in, never from the client.

    A cart line only stores a menu item ID and a quantity, so every price comes from
    menu_items. Lines whose menu item is missing from menu_items are left out, and the
    delivery fee is only charged when at least one line is priced.
    """
    lines = []
    for entry in cart.items:
        item = menu_items.get(entry.menu_item_id)
        if item is None:
            continue
        lines.append(CartLine(
            menu_item_id=item.id, name=item.name, unit_price=item.price,
            quantity=entry.quantity, line_total=round(item.price * entry.quantity, 2),
        ))
    subtotal = round(sum(line.line_total for line in lines), 2)
    fee = delivery_fee if lines else 0.0
    return CartView(
        id=cart.id, customer_id=cart.customer_id, restaurant_id=cart.restaurant_id,
        status=cart.status, items=lines, subtotal=subtotal,
        delivery_fee=fee, total=round(subtotal + fee, 2),
    )

