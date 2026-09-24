import json
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def sample_restaurants():
    return [
        {"id": 1, "name": "Test Pizza", "cuisine": "Italian", "rating": 4.5,
         "delivery_time_minutes": 25, "delivery_fee": 1.99,
         "address": "1 Test St", "is_open": True},
        {"id": 2, "name": "Test Sushi", "cuisine": "Japanese", "rating": 4.7,
         "delivery_time_minutes": 35, "delivery_fee": 2.99,
         "address": "2 Test St", "is_open": True},
    ]


@pytest.fixture
def temp_data_file(tmp_path, sample_restaurants):
    path = tmp_path / "restaurants.json"
    path.write_text(json.dumps(sample_restaurants), encoding="utf-8")
    return path


@pytest.fixture
def client(temp_data_file, monkeypatch):
    # CHANGE: env var name must match what your config in app/core uses
    monkeypatch.setenv("RESTAURANTS_DATA_PATH", str(temp_data_file))
    from app.main import app
    return TestClient(app)
