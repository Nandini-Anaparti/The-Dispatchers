import json
import pytest

def test_get_menu_items(tmp_path, monkeypatch, admin_client):
    file_path = tmp_path / "menu_items.json"

    items = [
        {
            "id": 1,
            "restaurant_id": 1,
            "name": "Pizza",
            "description": "Cheese pizza",
            "price": 12.99,
            "is_available": True
        }
    ]

    file_path.write_text(json.dumps(items))
    monkeypatch.setenv("MENU_ITEMS_DATA_PATH", str(file_path))

    response = admin_client.get("/restaurants/1/menu-items")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Pizza"

def test_get_menu_item(tmp_path, monkeypatch, admin_client):
    file_path = tmp_path / "menu_items.json"

    items = [
        {
            "id": 1,
            "restaurant_id": 1,
            "name": "Pizza",
            "description": "Cheese pizza",
            "price": 12.99,
            "is_available": True
        }
    ]

    file_path.write_text(json.dumps(items))
    monkeypatch.setenv("MENU_ITEMS_DATA_PATH", str(file_path))

    response = admin_client.get("/restaurants/1/menu-items/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_menu_item_not_found(tmp_path, monkeypatch, admin_client):
    file_path = tmp_path / "menu_items.json"
    file_path.write_text("[]")
    monkeypatch.setenv("MENU_ITEMS_DATA_PATH", str(file_path))

    response = admin_client.get("/restaurants/1/menu-items/999")

    assert response.status_code == 404

def test_menu_item_wrong_restaurant(tmp_path, monkeypatch, admin_client):
    file_path = tmp_path / "menu_items.json"

    items = [
        {
            "id": 1,
            "restaurant_id": 2,
            "name": "Sushi",
            "description": "Sushi roll",
            "price": 10.99,
            "is_available": True
        }
    ]

    file_path.write_text(json.dumps(items))
    monkeypatch.setenv("MENU_ITEMS_DATA_PATH", str(file_path))

    response = admin_client.get("/restaurants/1/menu-items/1")

    assert response.status_code == 404

    
def test_add_menu_item(tmp_path, monkeypatch, admin_client):
    file_path = tmp_path / "menu_items.json"
    file_path.write_text("[]")
    monkeypatch.setenv("MENU_ITEMS_DATA_PATH", str(file_path))

    new_item = {
        "name": "Pasta",
        "description": "Pasta with tomato sauce",
        "price": 15.99,
        "is_available": True
    }

    response = admin_client.post("/restaurants/1/menu-items", json=new_item)

    assert response.status_code == 201
    assert response.json()["name"] == "Pasta"
    assert response.json()["id"] == 1

    saved_items = json.loads(file_path.read_text())
    assert len(saved_items) == 1


def test_update_menu_item(tmp_path, monkeypatch, admin_client):
    file_path = tmp_path / "menu_items.json"

    items = [
        {
            "id": 1,
            "restaurant_id": 1,
            "name": "Pizza",
            "description": "Cheese pizza",
            "price": 12.99,
            "is_available": True
        }
    ]

    file_path.write_text(json.dumps(items))
    monkeypatch.setenv("MENU_ITEMS_DATA_PATH", str(file_path))

    updated_item = {
        "name": "Pepperoni Pizza",
        "description": "Pizza with pepperoni",
        "price": 14.99,
        "is_available": False
    }

    response = admin_client.put(
        "/restaurants/1/menu-items/1",
        json=updated_item
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Pepperoni Pizza"
    assert response.json()["price"] == 14.99
    assert response.json()["is_available"] is False

    saved_items = json.loads(file_path.read_text())
    assert saved_items[0]["name"] == "Pepperoni Pizza"
    assert saved_items[0]["is_available"] is False

def test_update_missing_item(tmp_path, monkeypatch, admin_client):
    file_path = tmp_path / "menu_items.json"
    file_path.write_text("[]")
    monkeypatch.setenv("MENU_ITEMS_DATA_PATH", str(file_path))

    updated_item = {
        "name": "Pizza",
        "description": "Cheese pizza",
        "price": 12.99,
        "is_available": True
    }

    response = admin_client.put(
        "/restaurants/1/menu-items/999",
        json=updated_item
    )

    assert response.status_code == 404

def test_add_invalid_price(tmp_path, monkeypatch, admin_client):
    file_path = tmp_path / "menu_items.json"
    file_path.write_text("[]")
    monkeypatch.setenv("MENU_ITEMS_DATA_PATH", str(file_path))

    new_item = {
        "name": "Pizza",
        "description": "Cheese pizza",
        "price": -5,
        "is_available": True
    }

    response = admin_client.post("/restaurants/1/menu-items", json=new_item)

    assert response.status_code == 422


def test_filter_by_price(tmp_path, monkeypatch, admin_client):
    file_path = tmp_path / "menu_items.json"

    items = [
        {
            "id": 1,
            "restaurant_id": 1,
            "name": "Pizza",
            "description": "Cheese pizza",
            "price": 15.99,
            "is_available": True
        },
        {
            "id": 2,
            "restaurant_id": 1,
            "name": "Garlic Bread",
            "description": "Garlic bread",
            "price": 5.99,
            "is_available": True
        }
    ]

    file_path.write_text(json.dumps(items))
    monkeypatch.setenv("MENU_ITEMS_DATA_PATH", str(file_path))

    response = admin_client.get("/restaurants/1/menu-items?max_price=10")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Garlic Bread"


def test_filter_by_availability(tmp_path, monkeypatch, admin_client):
    file_path = tmp_path / "menu_items.json"

    items = [
        {
            "id": 1,
            "restaurant_id": 1,
            "name": "Pizza",
            "description": "Cheese pizza",
            "price": 15.99,
            "is_available": True
        },
        {
            "id": 2,
            "restaurant_id": 1,
            "name": "Pasta",
            "description": "Tomato pasta",
            "price": 12.99,
            "is_available": False
        }
    ]

    file_path.write_text(json.dumps(items))
    monkeypatch.setenv("MENU_ITEMS_DATA_PATH", str(file_path))

    response = admin_client.get("/restaurants/1/menu-items?is_available=true")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Pizza"

def test_filter_by_name(tmp_path, monkeypatch, admin_client):
    file_path = tmp_path / "menu_items.json"

    items = [
        {
            "id": 1,
            "restaurant_id": 1,
            "name": "Cheese Pizza",
            "description": "Cheese pizza",
            "price": 12.99,
            "is_available": True
        },
        {
            "id": 2,
            "restaurant_id": 1,
            "name": "Pasta",
            "description": "Tomato pasta",
            "price": 11.99,
            "is_available": True
        }
    ]

    file_path.write_text(json.dumps(items))
    monkeypatch.setenv("MENU_ITEMS_DATA_PATH", str(file_path))

    response = admin_client.get("/restaurants/1/menu-items?name=PIZZA")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Cheese Pizza"

def test_deactivate_menu_item(tmp_path, monkeypatch, admin_client):
    file_path = tmp_path / "menu_items.json"

    items = [
        {
            "id": 1,
            "restaurant_id": 1,
            "name": "Pizza",
            "description": "Cheese pizza",
            "price": 12.99,
            "is_available": True
        },
        {
            "id": 2,
            "restaurant_id": 1,
            "name": "Pasta",
            "description": "Tomato pasta",
            "price": 10.99,
            "is_available": False
        }
    ]

    file_path.write_text(json.dumps(items))
    monkeypatch.setenv("MENU_ITEMS_DATA_PATH", str(file_path))

    response = admin_client.patch(
        "/restaurants/1/menu-items/1/deactivate"
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False
    assert response.json()["is_available"] is False

    saved_items = json.loads(file_path.read_text())

    assert len(saved_items) == 2
    assert saved_items[0]["is_active"] is False
    assert saved_items[0]["is_available"] is False

    response = admin_client.get("/restaurants/1/menu-items")

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [2]
    assert response.json()[0]["is_available"] is False

    response = admin_client.get(
        "/restaurants/1/menu-items/manage"
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [1, 2]

    assert admin_client.get(
        "/restaurants/1/menu-items/1"
    ).status_code == 404

    response = admin_client.put(
        "/restaurants/1/menu-items/1",
        json={
            "name": "Updated Pizza",
            "description": "Cheese pizza",
            "price": 14.99,
            "is_available": True
        }
    )

    assert response.status_code == 404
    
def test_deactivate_invalid_menu_item(tmp_path, monkeypatch, admin_client):
    file_path = tmp_path / "menu_items.json"

    items = [
        {
            "id": 1,
            "restaurant_id": 1,
            "name": "Pizza",
            "description": "Cheese pizza",
            "price": 12.99,
            "is_available": True
        }
    ]

    file_path.write_text(json.dumps(items))
    monkeypatch.setenv("MENU_ITEMS_DATA_PATH", str(file_path))

    response = admin_client.patch(
        "/restaurants/1/menu-items/999/deactivate"
    )

    assert response.status_code == 404

    response = admin_client.patch(
        "/restaurants/2/menu-items/1/deactivate"
    )

    assert response.status_code == 404

    assert json.loads(file_path.read_text()) == items
    
@pytest.mark.parametrize("method, url, body", [
    ("GET", "/restaurants/999/menu-items", None),
    ("GET", "/restaurants/999/menu-items/1", None),
    ("POST", "/restaurants/999/menu-items", {
        "name": "Pasta",
        "description": "Tomato pasta",
        "price": 12.99,
        "is_available": True
    }),
    ("PUT", "/restaurants/999/menu-items/1", {
        "name": "Pasta",
        "description": "Tomato pasta",
        "price": 12.99,
        "is_available": True
    }),
    ("PATCH", "/restaurants/999/menu-items/1/deactivate", None)
])

def test_missing_restaurant_returns_404(
    tmp_path, monkeypatch, admin_client, method, url, body
):
    file_path = tmp_path / "menu_items.json"

    items = [{
        "id": 1,
        "restaurant_id": 1,
        "name": "Pizza",
        "description": "Cheese pizza",
        "price": 12.99,
        "is_available": True
    }]

    file_path.write_text(json.dumps(items), encoding="utf-8")
    monkeypatch.setenv("MENU_ITEMS_DATA_PATH", str(file_path))

    original_data = file_path.read_text()

    response = admin_client.request(method, url, json=body)

    assert response.status_code == 404
    assert file_path.read_text() == original_data