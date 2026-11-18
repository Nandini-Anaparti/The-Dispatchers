import json
from pathlib import Path

from app.schemas.cart import Cart


class CartRepository:
    def __init__(self, data_path):
        self.data_path = Path(data_path)

    def get_all(self) -> list[Cart]:
        if not self.data_path.exists():
            raise FileNotFoundError(f"Cart data file not found: {self.data_path}")
        raw = json.loads(self.data_path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError("Cart data must be a JSON list")
        return [Cart(**record) for record in raw]

    def get_active_by_customer(self, customer_id: int) -> Cart | None:
        for cart in self.get_all():
            if cart.customer_id == customer_id and cart.status == "active":
                return cart
        return None

    def save_all(self, carts: list[Cart]) -> None:
        tmp = self.data_path.with_suffix(".tmp")
        tmp.write_text(json.dumps([c.model_dump() for c in carts], indent=2), encoding="utf-8")
        tmp.replace(self.data_path)

    def add(self, cart: Cart) -> Cart:
        carts = self.get_all()
        carts.append(cart)
        self.save_all(carts)
        return cart

    def update(self, cart: Cart) -> Cart | None:
        carts = self.get_all()
        for i, existing in enumerate(carts):
            if existing.id == cart.id:
                carts[i] = cart
                self.save_all(carts)
                return cart
        return None
    