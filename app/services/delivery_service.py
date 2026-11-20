"""Business rules for delivery creation."""

from app.schemas.delivery import Delivery, DeliveryCreate


class OrderNotFoundError(Exception):
    pass


class OrderNotEligibleError(Exception):
    pass


class ActiveDeliveryExistsError(Exception):
    pass


class DeliveryService:
    def __init__(self, delivery_repository, order_repository):
        self.delivery_repository = delivery_repository
        self.order_repository = order_repository

    def create_delivery(self, data: DeliveryCreate) -> Delivery:
        order = self.order_repository.get_by_id(data.order_id)

        if order is None:
            raise OrderNotFoundError(
                f"Order {data.order_id} not found"
            )

        if order.status != "ready":
            raise OrderNotEligibleError(
                f"Order {data.order_id} is not ready for delivery"
            )

        existing = self.delivery_repository.get_by_order(data.order_id)

        if any(delivery.status == "pending" for delivery in existing):
            raise ActiveDeliveryExistsError(
                f"Order {data.order_id} already has an active delivery"
            )

        deliveries = self.delivery_repository.get_all()
        next_id = max(
            (delivery.id for delivery in deliveries),
            default=0,
        ) + 1

        delivery = Delivery(
            id=next_id,
            order_id=data.order_id,
        )

        return self.delivery_repository.add(delivery)
