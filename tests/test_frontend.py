import pytest


def test_home_serves_frontend(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert 'id="restaurant-list"' in response.text
    assert 'href="/frontend/styles.css"' in response.text
    assert 'src="/frontend/browsing.js"' in response.text


@pytest.mark.parametrize(
    ("path", "content_type"),
    [
        ("/frontend/styles.css", "text/css"),
        ("/frontend/browsing.js", "javascript"),
    ],
)
def test_frontend_assets_are_served(client, path, content_type):
    response = client.get(path)

    assert response.status_code == 200
    assert content_type in response.headers["content-type"]
    assert response.content


def test_missing_frontend_file_returns_404(client):
    response = client.get("/frontend/missing-file.css")

    assert response.status_code == 404