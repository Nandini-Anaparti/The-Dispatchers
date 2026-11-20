from types import SimpleNamespace

import pytest

from app.repositories.delivery_repository import DeliveryRepository
from app.schemas.delivery import DeliveryCreate
from app.services.delivery_service import (
    ActiveDeliveryExistsError,
    DeliveryService,
    OrderNotEligibleError,
    OrderNotFoundError,
)


class FakeOrderRepository:
    def __init__(self, orders):
        self.orders = {order.id: order for order in orders}

    def get_by_id(self, order_id):
        return self.orders.get(order_id)


@pytest.fixture
def delivery_repository(tmp_path):
    data_path = tmp_path / "deliveries.json"
    data_path.write_text("[]", encoding="utf-8")
    return DeliveryRepository(data_path)


def test_create_delivery_for_ready_order(delivery_repository):
    order = SimpleNamespace(id=12, status="ready")
    order_repository = FakeOrderRepository([order])
    service = DeliveryService(delivery_repository, order_repository)

    delivery = service.create_delivery(DeliveryCreate(order_id=12))

    assert delivery.id == 1
    assert delivery.order_id == 12
    assert delivery.status == "pending"

    reloaded_repository = DeliveryRepository(
        delivery_repository.data_path
    )
    assert reloaded_repository.get_by_id(delivery.id) == delivery


def test_missing_order_does_not_change_storage(delivery_repository):
    order_repository = FakeOrderRepository([])
    service = DeliveryService(delivery_repository, order_repository)
    before = delivery_repository.data_path.read_bytes()

    with pytest.raises(OrderNotFoundError):
        service.create_delivery(DeliveryCreate(order_id=999))

    assert delivery_repository.data_path.read_bytes() == before


@pytest.mark.parametrize(
    "status",
    ["pending", "preparing", "cancelled", "delivered"],
)
def test_ineligible_order_does_not_change_storage(
    delivery_repository, status
):
    order = SimpleNamespace(id=12, status=status)
    service = DeliveryService(
        delivery_repository,
        FakeOrderRepository([order]),
    )
    before = delivery_repository.data_path.read_bytes()

    with pytest.raises(OrderNotEligibleError):
        service.create_delivery(DeliveryCreate(order_id=12))

    assert delivery_repository.data_path.read_bytes() == before


def test_duplicate_delivery_does_not_change_storage(
    delivery_repository,
):
    order = SimpleNamespace(id=12, status="ready")
    service = DeliveryService(
        delivery_repository,
        FakeOrderRepository([order]),
    )

    first_delivery = service.create_delivery(
        DeliveryCreate(order_id=12)
    )
    before = delivery_repository.data_path.read_bytes()

    with pytest.raises(ActiveDeliveryExistsError):
        service.create_delivery(DeliveryCreate(order_id=12))

    assert delivery_repository.data_path.read_bytes() == before
    assert delivery_repository.get_by_order(12) == [first_delivery]
