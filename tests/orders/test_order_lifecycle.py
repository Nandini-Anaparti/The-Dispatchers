"""ORDER-02: progress orders through their lifecycle."""

import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.order_service import (
    InvalidStatusTransitionError, OrderNotFoundError, OrderService,
)
from tests.orders.helpers import auth, move_to, place_orders

OWNER, OTHER_OWNER, ADMIN, CUSTOMER = 5, 6, 9, 1


@pytest.fixture
def client(order_env):
    with TestClient(app) as test_client:
        yield test_client


def status_url(order_id, restaurant_id=1):
    return f"/restaurants/{restaurant_id}/orders/{order_id}/status"


# ---- Service layer: the transition rules ----

def test_full_happy_path(order_env, priced_cart):
    service = OrderService(order_env.order_repo)
    order = place_orders(order_env, priced_cart)[0]
    order = move_to(service, order, "preparing", "ready", "delivered", "completed")
    assert order.status == "completed"


@pytest.mark.parametrize("path, bad_next", [
    ([], "ready"),                                   # cannot skip preparing
    ([], "completed"),                               # cannot jump to the end
    (["preparing"], "placed"),                       # cannot go backwards
    (["preparing", "ready"], "cancelled"),           # too late to cancel
    (["preparing", "ready", "delivered", "completed"], "preparing"),  # completed is final
    (["cancelled"], "placed"),                       # cancelled is final
    (["cancelled"], "preparing"),
])
def test_invalid_transitions_are_rejected(order_env, priced_cart, path, bad_next):
    service = OrderService(order_env.order_repo)
    order = move_to(service, place_orders(order_env, priced_cart)[0], *path)
    with pytest.raises(InvalidStatusTransitionError):
        service.update_status(1, order.id, bad_next)
    assert order_env.order_repo.get_by_id(order.id).status == order.status  # unchanged


def test_status_change_is_saved_to_json(order_env, priced_cart):
    order = place_orders(order_env, priced_cart)[0]
    OrderService(order_env.order_repo).update_status(1, order.id, "preparing")
    saved = json.loads((order_env.path / "orders.json").read_text())
    assert saved[0]["status"] == "preparing"


def test_order_from_another_restaurant_is_not_found(order_env, priced_cart):
    order = place_orders(order_env, priced_cart)[0]
    with pytest.raises(OrderNotFoundError):
        OrderService(order_env.order_repo).update_status(2, order.id, "preparing")


# ---- API: who can change statuses ----

def test_owner_updates_status(client, order_env, priced_cart):
    order = place_orders(order_env, priced_cart)[0]
    response = client.patch(status_url(order.id), json={"status": "preparing"}, headers=auth(OWNER))
    assert response.status_code == 200
    assert response.json()["status"] == "preparing"


def test_admin_updates_status(client, order_env, priced_cart):
    order = place_orders(order_env, priced_cart)[0]
    response = client.patch(status_url(order.id), json={"status": "preparing"}, headers=auth(ADMIN))
    assert response.status_code == 200


def test_invalid_transition_returns_409(client, order_env, priced_cart):
    order = place_orders(order_env, priced_cart)[0]
    response = client.patch(status_url(order.id), json={"status": "completed"}, headers=auth(OWNER))
    assert response.status_code == 409


def test_unknown_status_returns_422(client, order_env, priced_cart):
    order = place_orders(order_env, priced_cart)[0]
    response = client.patch(status_url(order.id), json={"status": "flying"}, headers=auth(OWNER))
    assert response.status_code == 422


def test_owner_of_another_restaurant_is_forbidden(client, order_env, priced_cart):
    order = place_orders(order_env, priced_cart)[0]
    response = client.patch(status_url(order.id), json={"status": "preparing"}, headers=auth(OTHER_OWNER))
    assert response.status_code == 403


def test_other_owner_cannot_reach_order_through_own_restaurant(client, order_env, priced_cart):
    order = place_orders(order_env, priced_cart)[0]  # belongs to restaurant 1
    response = client.patch(status_url(order.id, restaurant_id=2), json={"status": "preparing"},
                            headers=auth(OTHER_OWNER))
    assert response.status_code == 404
    assert order_env.order_repo.get_by_id(order.id).status == "placed"


def test_customer_cannot_change_status(client, order_env, priced_cart):
    order = place_orders(order_env, priced_cart)[0]
    response = client.patch(status_url(order.id), json={"status": "preparing"}, headers=auth(CUSTOMER))
    assert response.status_code == 403


def test_no_token_returns_401(client, order_env, priced_cart):
    order = place_orders(order_env, priced_cart)[0]
    assert client.patch(status_url(order.id), json={"status": "preparing"}).status_code == 401


def test_missing_order_returns_404(client):
    response = client.patch(status_url(999), json={"status": "preparing"}, headers=auth(OWNER))
    assert response.status_code == 404


def test_owner_lists_restaurant_orders_newest_first(client, order_env, priced_cart):
    place_orders(order_env, priced_cart, count=2)
    response = client.get("/restaurants/1/orders", headers=auth(OWNER))
    assert response.status_code == 200
    assert [o["id"] for o in response.json()] == [2, 1]


def test_customer_sees_new_status_in_their_history(client, order_env, priced_cart):
    order = place_orders(order_env, priced_cart)[0]
    client.patch(status_url(order.id), json={"status": "preparing"}, headers=auth(OWNER))
    response = client.get(f"/customers/1/orders/{order.id}", headers=auth(CUSTOMER))
    assert response.json()["status"] == "preparing"
