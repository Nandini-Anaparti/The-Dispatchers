"""Load and save delivery records using JSON."""

import json
from pathlib import Path

from app.schemas.delivery import Delivery


class DeliveryRepository:
    def __init__(self, data_path):
        self.data_path = Path(data_path)

    def get_all(self) -> list[Delivery]:
        with self.data_path.open("r", encoding="utf-8") as file:
            records = json.load(file)

        return [Delivery(**record) for record in records]

    def get_by_id(self, delivery_id: int) -> Delivery | None:
        for delivery in self.get_all():
            if delivery.id == delivery_id:
                return delivery

        return None

    def get_by_order(self, order_id: int) -> list[Delivery]:
        return [
            delivery
            for delivery in self.get_all()
            if delivery.order_id == order_id
        ]

    def add(self, delivery: Delivery) -> Delivery:
        deliveries = self.get_all()
        deliveries.append(delivery)
        self.save_all(deliveries)
        return delivery

    def save_all(self, deliveries: list[Delivery]) -> None:
        temporary_path = self.data_path.with_suffix(
            self.data_path.suffix + ".tmp"
        )

        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(
                [delivery.model_dump() for delivery in deliveries],
                file,
                indent=2,
            )

        temporary_path.replace(self.data_path)
