def test_get_restaurant_by_id_returns_restaurant(client):
    response = client.get("/restaurants/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Pizza"


def test_get_missing_restaurant_returns_404(client):
    response = client.get("/restaurants/999")
    assert response.status_code == 404


def test_get_restaurant_with_non_integer_id_returns_422(client):
    response = client.get("/restaurants/abc")
    assert response.status_code == 422
