def test_manage_page_is_served(client):
    response = client.get("/frontend/manage.html")
    assert response.status_code == 200
    assert "Manage Restaurants" in response.text
    