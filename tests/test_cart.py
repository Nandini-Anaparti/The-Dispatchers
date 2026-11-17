import json
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.routes.carts import get_cart_service
from app.repositories.cart_repository import CartRepository
from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.repositories.user_repository import UserRepository
from app.services.cart_service import CartService


def _restaurant(rid, fee):
    return {"id": rid, "name": f"R{rid}", "cuisine": "Italian", "rating": 4.0,
            "delivery_time_minutes": 20, "delivery_fee": fee, "address": "1 Main St", "is_open": True}


def _item(iid, rid, price, available=True):
    return {"id": iid, "restaurant_id": rid, "name": f"Item{iid}", "description": "d",
            "price": price, "is_available": available}


def _user(uid, active=True):
    return {"id": uid, "name": f"U{uid}", "email": f"u{uid}@x.com", "role": "customer",
            "is_active": active, "delivery_address": None, "password_hash": "x"}


@pytest.fixture
def client(tmp_path):
    files = {
        "restaurants.json": [_restaurant(1, 2.0), _restaurant(2, 3.0)],
        "menu.json": [_item(1, 1, 10.0), _item(2, 1, 5.0), _item(3, 2, 8.0), _item(4, 1, 7.0, False)],
        "users.json": [_user(1), _user(2, active=False)],
        "carts.json": [],
    }
    for name, data in files.items():
        (tmp_path / name).write_text(json.dumps(data))

    def override():
        return CartService(
            CartRepository(tmp_path / "carts.json"),
            MenuItemRepository(tmp_path / "menu.json"),
            RestaurantRepository(tmp_path / "restaurants.json"),
            UserRepository(tmp_path / "users.json"),
        )

    app.dependency_overrides[get_cart_service] = override
    c = TestClient(app)
    c.tmp_path = tmp_path
    yield c
    app.dependency_overrides.clear()


def test_new_customer_gets_empty_cart(client):
    r = client.get("/customers/1/cart")
    assert r.status_code == 200
    assert r.json()["items"] == [] and r.json()["total"] == 0


def test_only_one_active_cart_per_customer(client):
    client.get("/customers/1/cart")
    client.get("/customers/1/cart")
    saved = json.loads((client.tmp_path / "carts.json").read_text())
    assert len(saved) == 1


def test_add_items_and_backend_totals(client):
    client.post("/customers/1/cart/items", json={"menu_item_id": 1, "quantity": 2})
    r = client.post("/customers/1/cart/items", json={"menu_item_id": 2, "quantity": 1})
    body = r.json()
    assert body["subtotal"] == 25.0 and body["delivery_fee"] == 2.0 and body["total"] == 27.0


def test_adding_same_item_increases_quantity(client):
    client.post("/customers/1/cart/items", json={"menu_item_id": 1, "quantity": 1})
    r = client.post("/customers/1/cart/items", json={"menu_item_id": 1, "quantity": 2})
    assert len(r.json()["items"]) == 1 and r.json()["items"][0]["quantity"] == 3


def test_update_remove_and_clear(client):
    client.post("/customers/1/cart/items", json={"menu_item_id": 1, "quantity": 1})
    assert client.put("/customers/1/cart/items/1", json={"quantity": 4}).json()["subtotal"] == 40.0
    assert client.delete("/customers/1/cart/items/1").json()["items"] == []
    client.post("/customers/1/cart/items", json={"menu_item_id": 2, "quantity": 1})
    cleared = client.delete("/customers/1/cart").json()
    assert cleared["items"] == [] and cleared["total"] == 0


def test_remove_item_not_in_cart_404(client):
    assert client.delete("/customers/1/cart/items/1").status_code == 404


def test_cart_persists_across_service_instances(client):
    client.post("/customers/1/cart/items", json={"menu_item_id": 1, "quantity": 2})
    saved = json.loads((client.tmp_path / "carts.json").read_text())
    assert saved[0]["items"] == [{"menu_item_id": 1, "quantity": 2}]


def test_unavailable_item_rejected(client):
    r = client.post("/customers/1/cart/items", json={"menu_item_id": 4, "quantity": 1})
    assert r.status_code == 409


def test_cannot_mix_restaurants(client):
    client.post("/customers/1/cart/items", json={"menu_item_id": 1, "quantity": 1})
    r = client.post("/customers/1/cart/items", json={"menu_item_id": 3, "quantity": 1})
    assert r.status_code == 409


def test_invalid_quantity_rejected(client):
    r = client.post("/customers/1/cart/items", json={"menu_item_id": 1, "quantity": 0})
    assert r.status_code == 422


def test_deactivated_customer_blocked(client):
    assert client.get("/customers/2/cart").status_code == 403
    assert client.post("/customers/2/cart/items", json={"menu_item_id": 1, "quantity": 1}).status_code == 403


def test_unknown_customer_and_item(client):
    assert client.get("/customers/99/cart").status_code == 404
    assert client.post("/customers/1/cart/items", json={"menu_item_id": 99, "quantity": 1}).status_code == 404
    