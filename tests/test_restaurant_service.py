"""Unit tests for RestaurantService filtering, without going through the API.

A small fake repository stands in for the JSON file, so these tests check the
service-layer logic on its own.
"""

from app.schemas.restaurant import Restaurant
from app.services.restaurant_service import RestaurantService


class FakeRepository:
    def __init__(self, restaurants):
        self.restaurants = restaurants

    def get_all(self):
        return list(self.restaurants)


def make_service():
    restaurants = [
        Restaurant(id=1, name="Test Pizza", cuisine="Italian", rating=4.5,
                   delivery_time_minutes=25, delivery_fee=1.99, address="1 Test St", is_open=True),
        Restaurant(id=2, name="Test Sushi", cuisine="Japanese", rating=4.7,
                   delivery_time_minutes=35, delivery_fee=2.99, address="2 Test St", is_open=True),
        Restaurant(id=3, name="Pizza Palace", cuisine="Italian", rating=3.9,
                   delivery_time_minutes=30, delivery_fee=0.99, address="3 Test St", is_open=False),
    ]
    return RestaurantService(FakeRepository(restaurants))


def ids(restaurants):
    return [r.id for r in restaurants]


def test_service_no_filters_returns_all():
    assert ids(make_service().list_restaurants()) == [1, 2, 3]


def test_service_name_filter_is_partial_and_case_insensitive():
    assert ids(make_service().list_restaurants(name="PIZZA")) == [1, 3]


def test_service_cuisine_filter_is_case_insensitive():
    assert ids(make_service().list_restaurants(cuisine="italian")) == [1, 3]


def test_service_is_open_filter():
    assert ids(make_service().list_restaurants(is_open=False)) == [3]


def test_service_min_rating_includes_exact_match():
    assert ids(make_service().list_restaurants(min_rating=4.5)) == [1, 2]


def test_service_combined_filters():
    assert ids(make_service().list_restaurants(cuisine="Italian", is_open=True)) == [1]


def test_service_no_matches_returns_empty_list():
    assert make_service().list_restaurants(name="burger") == []
