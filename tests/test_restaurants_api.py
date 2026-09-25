def test_list_restaurants_returns_data(client, sample_restaurants):
    response = client.get("/restaurants") 
    assert response.status_code == 200
    data = response.json()
    assert data == sample_restaurants


def test_list_restaurants_returns_empty_list(client, temp_data_file):
    temp_data_file.write_text("[]", encoding="utf-8")

    response = client.get("/restaurants")

    assert response.status_code == 200
    assert response.json() == []


def test_restaurants_have_required_fields(client):
    data = client.get("/restaurants").json() 
    for r in data:
        assert "id" in r
        assert "name" in r
        assert "cuisine" in r
