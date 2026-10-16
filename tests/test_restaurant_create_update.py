"""Tests for creating (POST) and updating (PUT) restaurants."""

import json

from app.repositories.restaurant_repository import RestaurantRepository
from app.schemas.restaurant import Restaurant

NEW_RESTAURANT = {
    "name": "Test Tacos",
    "cuisine": "Mexican",
    "delivery_time_minutes": 20,
    "delivery_fee": 1.49,
    "address": "3 Test St",
}


# ---- create ----

def test_create_restaurant_returns_201_with_next_id(client):
    response = client.post("/restaurants", json=NEW_RESTAURANT)
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 3  # sample data has ids 1 and 2
    assert body["name"] == "Test Tacos"
    assert body["is_open"] is True  # default
    assert body["rating"] == 0  # default


def test_created_restaurant_is_saved_to_file(client, temp_data_file):
    client.post("/restaurants", json=NEW_RESTAURANT)
    saved = json.loads(temp_data_file.read_text(encoding="utf-8"))
    assert len(saved) == 3
    assert saved[-1]["name"] == "Test Tacos"
    # and it shows up through the API too
    assert client.get("/restaurants/3").json()["name"] == "Test Tacos"


def test_create_restaurant_missing_field_returns_422(client):
    bad = {k: v for k, v in NEW_RESTAURANT.items() if k != "name"}
    response = client.post("/restaurants", json=bad)
    assert response.status_code == 422


def test_create_restaurant_negative_fee_returns_422(client):
    response = client.post("/restaurants", json={**NEW_RESTAURANT, "delivery_fee": -1})
    assert response.status_code == 422


# ---- update ----

def test_update_changes_only_sent_fields(client):
    response = client.put("/restaurants/1", json={"is_open": False, "delivery_fee": 0.99})
    assert response.status_code == 200
    body = response.json()
    assert body["is_open"] is False
    assert body["delivery_fee"] == 0.99
    assert body["name"] == "Test Pizza"  # untouched


def test_update_is_saved_to_file(client, temp_data_file):
    client.put("/restaurants/2", json={"name": "Renamed Sushi"})
    saved = json.loads(temp_data_file.read_text(encoding="utf-8"))
    assert saved[1]["name"] == "Renamed Sushi"
    assert saved[0]["name"] == "Test Pizza"  # other restaurant unchanged


def test_update_missing_restaurant_returns_404(client):
    response = client.put("/restaurants/999", json={"name": "Ghost"})
    assert response.status_code == 404


def test_update_invalid_rating_returns_422(client):
    response = client.put("/restaurants/1", json={"rating": 7})
    assert response.status_code == 422


# ---- repository unit tests ----

def test_repository_add_and_update(temp_data_file):
    repo = RestaurantRepository(temp_data_file)
    new = Restaurant(id=3, **{**NEW_RESTAURANT, "rating": 4.0, "is_open": True})
    repo.add(new)
    assert repo.get_by_id(3).name == "Test Tacos"

    repo.update(new.model_copy(update={"name": "Tacos Two"}))
    assert repo.get_by_id(3).name == "Tacos Two"
    assert len(repo.get_all()) == 3


def test_repository_update_unknown_id_returns_none(temp_data_file):
    repo = RestaurantRepository(temp_data_file)
    ghost = Restaurant(id=999, **{**NEW_RESTAURANT, "rating": 4.0, "is_open": True})
    assert repo.update(ghost) is None
