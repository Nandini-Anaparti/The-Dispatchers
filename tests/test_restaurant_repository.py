import json
import pytest

from app.repositories.restaurant_repository import RestaurantRepository


def test_repository_returns_all_restaurants(temp_data_file, sample_restaurants):
    original = temp_data_file.read_bytes()
    repo = RestaurantRepository(temp_data_file) 
    restaurants = repo.get_all()  
    assert [restaurant.model_dump() for restaurant in restaurants] == sample_restaurants
    assert temp_data_file.read_bytes() == original


def test_repository_missing_file_fails(tmp_path):
    repo = RestaurantRepository(tmp_path / "does_not_exist.json")
    with pytest.raises(FileNotFoundError):
        repo.get_all()


def test_repository_invalid_json_fails(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{ not valid json", encoding="utf-8")
    repo = RestaurantRepository(bad)
    with pytest.raises(ValueError): 
        repo.get_all()


def test_repository_empty_list(temp_data_file):
    temp_data_file.write_text("[]", encoding="utf-8")
    assert RestaurantRepository(temp_data_file).get_all() == []


@pytest.mark.parametrize("data", [{"restaurants": []}, [{"id": 1}]],
                         ids=["not-a-list", "missing-required-fields"])
def test_repository_invalid_structure_fails(temp_data_file, data):
    temp_data_file.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError):
        RestaurantRepository(temp_data_file).get_all()


def test_repository_get_by_id(temp_data_file, sample_restaurants):
    restaurant = RestaurantRepository(temp_data_file).get_by_id(2)

    assert restaurant is not None
    assert restaurant.model_dump() == sample_restaurants[1]


def test_repository_missing_id_returns_none(temp_data_file):
    assert RestaurantRepository(temp_data_file).get_by_id(999) is None
      
