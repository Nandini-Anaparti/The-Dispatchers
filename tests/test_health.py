def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200
