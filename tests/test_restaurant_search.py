"""Tests for searching and filtering restaurants (GET /restaurants?...)."""

import json

import pytest


@pytest.fixture
def filter_data(temp_data_file):
    """Overwrite the temp data file with a bigger mix of restaurants."""
    data = [
        {"id": 1, "name": "Test Pizza", "cuisine": "Italian", "rating": 4.5,
         "delivery_time_minutes": 25, "delivery_fee": 1.99, "address": "1 Test St", "is_open": True},
        {"id": 2, "name": "Test Sushi", "cuisine": "Japanese", "rating": 4.7,
         "delivery_time_minutes": 35, "delivery_fee": 2.99, "address": "2 Test St", "is_open": True},
        {"id": 3, "name": "Pizza Palace", "cuisine": "Italian", "rating": 3.9,
         "delivery_time_minutes": 30, "delivery_fee": 0.99, "address": "3 Test St", "is_open": False},
    ]
    temp_data_file.write_text(json.dumps(data), encoding="utf-8")
    return data


def ids(response):
    return [r["id"] for r in response.json()]


def test_no_filters_returns_everything(client, filter_data):
    response = client.get("/restaurants")
    assert response.status_code == 200
    assert ids(response) == [1, 2, 3]


def test_filter_by_name_is_partial_and_case_insensitive(client, filter_data):
    response = client.get("/restaurants", params={"name": "PIZZA"})
    assert response.status_code == 200
    assert ids(response) == [1, 3]


def test_filter_by_cuisine(client, filter_data):
    response = client.get("/restaurants", params={"cuisine": "japanese"})
    assert ids(response) == [2]


def test_filter_by_is_open(client, filter_data):
    response = client.get("/restaurants", params={"is_open": "false"})
    assert ids(response) == [3]


def test_filter_by_min_rating(client, filter_data):
    response = client.get("/restaurants", params={"min_rating": 4.5})
    assert ids(response) == [1, 2]


def test_filters_combine(client, filter_data):
    response = client.get("/restaurants", params={"cuisine": "Italian", "is_open": "true"})
    assert ids(response) == [1]


def test_no_matches_returns_empty_list(client, filter_data):
    response = client.get("/restaurants", params={"name": "burger"})
    assert response.status_code == 200
    assert response.json() == []


def test_invalid_min_rating_returns_422(client, filter_data):
    response = client.get("/restaurants", params={"min_rating": 9})
    assert response.status_code == 422
