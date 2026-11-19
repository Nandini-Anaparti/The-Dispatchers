"""ORDER-01: retrieve individual orders and customer order history."""

import json
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.core.auth import create_access_token
from app.main import app
from app.services.order_service import OrderService

URL = "/customers/{}/orders"


@pytest.fixture
def client(order_env):
    with TestClient(app) as test_client:
        yield test_client


def auth(user_id):
    return {"Authorization": f"Bearer {create_access_token(user_id)}"}


def place(order_env, priced_cart, customer_id=1, count=1):
    """Create orders through CHECKOUT-03 with a clock that moves 1 minute each time."""
    ticks = iter(datetime(2026, 11, 18, tzinfo=timezone.utc) + timedelta(minutes=i) for i in range(10))
    service = OrderService(order_env.order_repo, now=lambda: next(ticks))
    cart = priced_cart.model_copy(update={"customer_id": customer_id})
    return [service.create_order(cart) for _ in range(count)]


def test_get_one_order_with_items_prices_total_status(client, order_env, priced_cart):
    order = place(order_env, priced_cart)[0]
    response = client.get(URL.format(1) + f"/{order.id}", headers=auth(1))
    assert response.status_code == 200
    body = response.json()
    assert [(i["menu_item_id"], i["quantity"], i["unit_price"]) for i in body["items"]] == [(1, 2, 10.0), (2, 1, 5.0)]
    assert body["total"] == 27.0
    assert body["status"] == "placed"


def test_order_history_newest_first(client, order_env, priced_cart):
    place(order_env, priced_cart, count=3)
    response = client.get(URL.format(1), headers=auth(1))
    assert response.status_code == 200
    assert [o["id"] for o in response.json()] == [3, 2, 1]


def test_order_history_empty(client):
    response = client.get(URL.format(1), headers=auth(1))
    assert response.status_code == 200
    assert response.json() == []


def test_history_only_has_own_orders(client, order_env, priced_cart):
    place(order_env, priced_cart, customer_id=2)
    assert client.get(URL.format(1), headers=auth(1)).json() == []


def test_nonexistent_order_returns_404(client):
    assert client.get(URL.format(1) + "/999", headers=auth(1)).status_code == 404


def test_another_customers_order_returns_404(client, order_env, priced_cart):
    other = place(order_env, priced_cart, customer_id=2)[0]
    assert client.get(URL.format(1) + f"/{other.id}", headers=auth(1)).status_code == 404


def test_cannot_use_another_customers_url(client, order_env, priced_cart):
    place(order_env, priced_cart)
    assert client.get(URL.format(1), headers=auth(2)).status_code == 403
    assert client.get(URL.format(1) + "/1", headers=auth(2)).status_code == 403


def test_admin_token_cannot_read_customer_orders(client):
    assert client.get(URL.format(9), headers=auth(9)).status_code == 403


def test_no_token_returns_401(client):
    assert client.get(URL.format(1)).status_code == 401


def test_orders_still_there_after_restart(order_env, priced_cart):
    place(order_env, priced_cart)
    # A new TestClient builds everything from scratch, like restarting the app
    with TestClient(app) as fresh:
        assert len(fresh.get(URL.format(1), headers=auth(1)).json()) == 1


def test_history_displays_saved_order_prices_after_menu_changes(client, order_env, priced_cart):
    order = place(order_env, priced_cart)[0]
    menu_path = order_env.path / "menu_items.json"
    menu = json.loads(menu_path.read_text(encoding="utf-8"))
    menu[0].update(name="New menu name", price=99.0, is_available=False)
    menu_path.write_text(json.dumps(menu), encoding="utf-8")

    response = client.get(URL.format(1), headers=auth(1))
    assert response.status_code == 200
    assert response.json() == [order.model_dump(mode="json")]


def test_order_history_page_serves_its_script(client):
    page = client.get("/frontend/orders.html")
    assert page.status_code == 200
    assert 'id="order-history"' in page.text
    assert 'src="/frontend/orders.js"' in page.text

    script = client.get("/frontend/orders.js")
    assert script.status_code == 200
    assert "javascript" in script.headers["content-type"]
