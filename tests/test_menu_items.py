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
