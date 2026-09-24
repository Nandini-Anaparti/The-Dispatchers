import json
import pytest

from app.repositories.restaurant_repository import RestaurantRepository


def test_repository_returns_all_restaurants(temp_data_file):
    repo = RestaurantRepository(temp_data_file) 
    restaurants = repo.get_all()  
    assert len(restaurants) == 2


def test_repository_missing_file_fails(tmp_path):
    repo = RestaurantRepository(tmp_path / "does_not_exist.json")
    with pytest.raises((FileNotFoundError, ValueError)):
        repo.get_all()


def test_repository_invalid_json_fails(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{ not valid json", encoding="utf-8")
    repo = RestaurantRepository(bad)
    with pytest.raises(ValueError): 
        repo.get_all()
      
