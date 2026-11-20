"""ORDER-03: customers cancel eligible orders."""

import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.order_repository import OrderRepository
from app.repositories.user_repository import UserRepository
from app.services.order_service import OrderNotCancellableError, OrderNotFoundError, OrderService
from tests.orders.helpers import auth, move_to, place_orders


@pytest.fixture
def client(order_env):
    with TestClient(app) as test_client:
        yield test_client


def service_for(order_env):
    return OrderService(order_env.order_repo, user_repo=UserRepository(order_env.path / "users.json"))


def cancel_url(order_id, customer_id=1):
    return f"/customers/{customer_id}/orders/{order_id}/cancel"


# ---- Service layer ----

def test_placed_order_can_be_cancelled(order_env, priced_cart):
    order = place_orders(order_env, priced_cart)[0]
    cancelled = service_for(order_env).cancel_order(1, order.id)
    assert cancelled.status == "cancelled"


@pytest.mark.parametrize("path", [
    ["preparing"],
    ["preparing", "ready"],
    ["preparing", "ready", "delivered", "completed"],
    ["cancelled"],  # already cancelled
])
def test_orders_past_placed_cannot_be_cancelled(order_env, priced_cart, path):
    service = service_for(order_env)
    order = move_to(service, place_orders(order_env, priced_cart)[0], *path)
    with pytest.raises(OrderNotCancellableError):
        service.cancel_order(1, order.id)
    assert order_env.order_repo.get_by_id(order.id).status == order.status  # unchanged


def test_cannot_cancel_another_customers_order(order_env, priced_cart):
    order = place_orders(order_env, priced_cart, customer_id=2)[0]
    with pytest.raises(OrderNotFoundError):
        service_for(order_env).cancel_order(1, order.id)
    assert order_env.order_repo.get_by_id(order.id).status == "placed"


def test_cancelled_order_stays_saved_after_restart(order_env, priced_cart):
    order = place_orders(order_env, priced_cart)[0]
    service_for(order_env).cancel_order(1, order.id)
    reloaded = OrderRepository(order_env.path / "orders.json").get_by_id(order.id)
    assert reloaded.status == "cancelled"
    assert reloaded.total == 27.0


# ---- API ----

def test_cancel_through_api(client, order_env, priced_cart):
    order = place_orders(order_env, priced_cart)[0]
    response = client.post(cancel_url(order.id), headers=auth(1))
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
    saved = json.loads((order_env.path / "orders.json").read_text())
    assert saved[0]["status"] == "cancelled"


def test_cancel_preparing_order_returns_409(client, order_env, priced_cart):
    order = move_to(service_for(order_env), place_orders(order_env, priced_cart)[0], "preparing")
    assert client.post(cancel_url(order.id), headers=auth(1)).status_code == 409


def test_cancel_missing_order_returns_404(client):
    assert client.post(cancel_url(999), headers=auth(1)).status_code == 404


def test_cancel_with_another_customers_token_returns_403(client, order_env, priced_cart):
    order = place_orders(order_env, priced_cart)[0]
    assert client.post(cancel_url(order.id), headers=auth(2)).status_code == 403


def test_cancel_without_token_returns_401(client, order_env, priced_cart):
    order = place_orders(order_env, priced_cart)[0]
    assert client.post(cancel_url(order.id)).status_code == 401


def test_cancelled_order_still_in_history(client, order_env, priced_cart):
    order = place_orders(order_env, priced_cart)[0]
    client.post(cancel_url(order.id), headers=auth(1))
    history = client.get("/customers/1/orders", headers=auth(1)).json()
    assert [(o["id"], o["status"]) for o in history] == [(order.id, "cancelled")]
