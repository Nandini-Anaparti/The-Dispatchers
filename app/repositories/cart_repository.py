import json
from collections.abc import Callable
from pathlib import Path
from threading import RLock

from app.schemas.cart import Cart

# Requests use separate repository instances within the same API process.
_cart_file_lock = RLock()


class CartRepository:
    def __init__(self, data_path):
        self.data_path = Path(data_path)

    def get_all(self) -> list[Cart]:
        with _cart_file_lock:
            if not self.data_path.exists():
                raise FileNotFoundError(f"Cart data file not found: {self.data_path}")
            raw = json.loads(self.data_path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError("Cart data must be a JSON list")
        return [Cart(**record) for record in raw]

    def get_active_by_customer(self, customer_id: int) -> Cart | None:
        return self._find_active(self.get_all(), customer_id)

    @staticmethod
    def _find_active(carts: list[Cart], customer_id: int) -> Cart | None:
        return next(
            (cart for cart in carts if cart.customer_id == customer_id and cart.status == "active"),
            None,
        )

    def get_or_create_active(self, customer_id: int) -> Cart:
        with _cart_file_lock:
            carts = self.get_all()
            existing = self._find_active(carts, customer_id)
            if existing is not None:
                return existing

            cart = self._new_active(carts, customer_id)
            carts.append(cart)
            self.save_all(carts)
            return cart

    @staticmethod
    def _new_active(carts: list[Cart], customer_id: int) -> Cart:
        next_id = max((cart.id for cart in carts), default=0) + 1
        return Cart(id=next_id, customer_id=customer_id)

    def mutate_active(
        self, customer_id: int, change: Callable[[Cart], None], *, create: bool = False
    ) -> Cart | None:
        """Apply a change to the latest active cart and save only on success."""
        with _cart_file_lock:
            carts = self.get_all()
            cart = self._find_active(carts, customer_id)
            if cart is None:
                if not create:
                    return None
                cart = self._new_active(carts, customer_id)
                carts.append(cart)

            change(cart)
            self.save_all(carts)
            return cart

    def save_all(self, carts: list[Cart]) -> None:
        with _cart_file_lock:
            tmp = self.data_path.with_suffix(".tmp")
            tmp.write_text(json.dumps([c.model_dump() for c in carts], indent=2), encoding="utf-8")
            tmp.replace(self.data_path)

    def add(self, cart: Cart) -> Cart:
        with _cart_file_lock:
            carts = self.get_all()
            carts.append(cart)
            self.save_all(carts)
        return cart

    def update(self, cart: Cart) -> Cart | None:
        with _cart_file_lock:
            carts = self.get_all()
            for i, existing in enumerate(carts):
                if existing.id == cart.id:
                    carts[i] = cart
                    self.save_all(carts)
                    return cart
        return None
