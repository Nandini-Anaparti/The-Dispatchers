import json

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_menu_items(tmp_path, monkeypatch):
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

    response = client.get("/restaurants/1/menu-items")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Pizza"

def test_get_menu_item(tmp_path, monkeypatch):
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

    response = client.get("/restaurants/1/menu-items/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_menu_item_not_found(tmp_path, monkeypatch):
    file_path = tmp_path / "menu_items.json"
    file_path.write_text("[]")
    monkeypatch.setenv("MENU_ITEMS_DATA_PATH", str(file_path))

    response = client.get("/restaurants/1/menu-items/999")

    assert response.status_code == 404

def test_menu_item_wrong_restaurant(tmp_path, monkeypatch):
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

    response = client.get("/restaurants/1/menu-items/1")

    assert response.status_code == 404

    
def test_add_menu_item(tmp_path, monkeypatch):
    file_path = tmp_path / "menu_items.json"
    file_path.write_text("[]")
    monkeypatch.setenv("MENU_ITEMS_DATA_PATH", str(file_path))

    new_item = {
        "name": "Pasta",
        "description": "Pasta with tomato sauce",
        "price": 15.99,
        "is_available": True
    }

    response = client.post("/restaurants/1/menu-items", json=new_item)

    assert response.status_code == 201
    assert response.json()["name"] == "Pasta"
    assert response.json()["id"] == 1

    saved_items = json.loads(file_path.read_text())
    assert len(saved_items) == 1


def test_update_menu_item(tmp_path, monkeypatch):
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

    response = client.put(
        "/restaurants/1/menu-items/1",
        json=updated_item
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Pepperoni Pizza"
    assert response.json()["price"] == 14.99

    saved_items = json.loads(file_path.read_text())
    assert saved_items[0]["name"] == "Pepperoni Pizza"


def test_update_missing_item(tmp_path, monkeypatch):
    file_path = tmp_path / "menu_items.json"
    file_path.write_text("[]")
    monkeypatch.setenv("MENU_ITEMS_DATA_PATH", str(file_path))

    updated_item = {
        "name": "Pizza",
        "description": "Cheese pizza",
        "price": 12.99,
        "is_available": True
    }

    response = client.put(
        "/restaurants/1/menu-items/999",
        json=updated_item
    )

    assert response.status_code == 404

def test_add_invalid_price(tmp_path, monkeypatch):
    file_path = tmp_path / "menu_items.json"
    file_path.write_text("[]")
    monkeypatch.setenv("MENU_ITEMS_DATA_PATH", str(file_path))

    new_item = {
        "name": "Pizza",
        "description": "Cheese pizza",
        "price": -5,
        "is_available": True
    }

    response = client.post("/restaurants/1/menu-items", json=new_item)

    assert response.status_code == 422