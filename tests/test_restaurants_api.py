def test_list_restaurants_returns_data(client):  
    response = client.get("/restaurants") 
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Test Pizza"


def test_restaurants_have_required_fields(client):
    data = client.get("/restaurants").json() 
    for r in data:
        assert "id" in r
        assert "name" in r
        assert "cuisine" in r
