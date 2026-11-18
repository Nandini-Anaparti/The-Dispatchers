"""The only code that reads and writes data/orders.json."""

import json
from pathlib import Path
from threading import RLock

from app.schemas.order import Order

_orders_lock = RLock()


class OrderRepository:
    def __init__(self, data_path):
        self.data_path = Path(data_path)

    def get_all(self) -> list[Order]:
        with _orders_lock:
            if not self.data_path.exists():
                return []
            raw = json.loads(self.data_path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError("Order data must be a JSON list")
        return [Order(**record) for record in raw]

    def get_by_id(self, order_id: int) -> Order | None:
        return next((o for o in self.get_all() if o.id == order_id), None)

    def get_by_customer(self, customer_id: int) -> list[Order]:
        return [o for o in self.get_all() if o.customer_id == customer_id]

    def add(self, **fields) -> Order:
        """Give the order the next unique ID and save it. IDs are never reused."""
        with _orders_lock:
            orders = self.get_all()
            next_id = max((o.id for o in orders), default=0) + 1
            order = Order(id=next_id, **fields)
            orders.append(order)
            self._save_all(orders)
        return order

    def _save_all(self, orders: list[Order]) -> None:
        with _orders_lock:
            tmp = self.data_path.with_suffix(".tmp")
            tmp.write_text(
                json.dumps([o.model_dump(mode="json") for o in orders], indent=2),
                encoding="utf-8",
            )
            tmp.replace(self.data_path)  # atomic: the file is never half-written
