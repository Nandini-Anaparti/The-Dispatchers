"""ORDER-04: completed and cancelled orders are preserved exactly as they were at checkout."""

import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.order_repository import OrderRepository
from app.repositories.user_repository import UserRepository
from app.services.order_service import OrderService
from tests.orders.helpers import auth, move_to, place_orders

COMPLETE = ["preparing", "ready", "delivered", "completed"]


@pytest.fixture
def client(order_env):
    with TestClient(app) as test_client:
        yield test_client


def make_history(order_env, priced_cart):
    """One completed order and one cancelled order for customer 1."""
    service = OrderService(order_env.order_repo, user_repo=UserRepository(order_env.path / "users.json"))
    completed, cancelled = place_orders(order_env, priced_cart, count=2)
    completed = move_to(service, completed, *COMPLETE)
    cancelled = service.cancel_order(1, cancelled.id)
    return completed, cancelled


def change_menu(order_env, **changes):
    """Simulate the restaurant editing Item1 after the orders were placed."""
    menu = json.loads((order_env.path / "menu_items.json").read_text())
    menu[0].update(changes)
    (order_env.path / "menu_items.json").write_text(json.dumps(menu))


def test_completed_and_cancelled_orders_are_retrievable(client, order_env, priced_cart):
    completed, cancelled = make_history(order_env, priced_cart)
    for order in (completed, cancelled):
        response = client.get(f"/customers/1/orders/{order.id}", headers=auth(1))
        assert response.status_code == 200
    statuses = {o["id"]: o["status"] for o in client.get("/customers/1/orders", headers=auth(1)).json()}
    assert statuses == {completed.id: "completed", cancelled.id: "cancelled"}


def test_items_quantities_and_prices_unchanged_after_lifecycle(order_env, priced_cart):
    original = place_orders(order_env, priced_cart)[0]
    service = OrderService(order_env.order_repo)
    final = move_to(service, original, *COMPLETE)
    # Everything except the status is exactly what was saved at checkout
    assert final.model_dump(exclude={"status"}) == original.model_dump(exclude={"status"})


def test_menu_price_change_does_not_change_old_orders(client, order_env, priced_cart):
    completed, cancelled = make_history(order_env, priced_cart)
    change_menu(order_env, price=99.0, name="Renamed Item")

    for order in (completed, cancelled):
        body = client.get(f"/customers/1/orders/{order.id}", headers=auth(1)).json()
        assert body["items"][0]["unit_price"] == 10.0
        assert body["items"][0]["name"] == "Item1"
        assert body["total"] == 27.0


def test_deactivated_menu_item_does_not_change_old_orders(client, order_env, priced_cart):
    completed, _ = make_history(order_env, priced_cart)
    change_menu(order_env, is_available=False, is_active=False)
    body = client.get(f"/customers/1/orders/{completed.id}", headers=auth(1)).json()
    assert [i["menu_item_id"] for i in body["items"]] == [1, 2]


def test_history_survives_restart(order_env, priced_cart):
    completed, cancelled = make_history(order_env, priced_cart)
    # A brand-new repository only has the JSON file to go on, like a restarted app
    reloaded = OrderRepository(order_env.path / "orders.json")
    assert reloaded.get_by_id(completed.id) == completed
    assert reloaded.get_by_id(cancelled.id) == cancelled


def test_history_through_api_after_restart(order_env, priced_cart):
    make_history(order_env, priced_cart)
    with TestClient(app) as fresh:
        statuses = sorted(o["status"] for o in fresh.get("/customers/1/orders", headers=auth(1)).json())
    assert statuses == ["cancelled", "completed"]


def test_repository_status_update_cannot_touch_items(order_env, priced_cart):
    """The repository only exposes update_status, so a status change can never rewrite prices."""
    order = place_orders(order_env, priced_cart)[0]
    updated = order_env.order_repo.update_status(order.id, "preparing")
    assert updated.items == order.items
    assert updated.total == order.total
    assert not hasattr(order_env.order_repo, "update")
