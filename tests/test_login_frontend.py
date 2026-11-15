import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def login_client(tmp_path, monkeypatch):
    users_path = tmp_path / "users.json"
    users_path.write_text("[]", encoding="utf-8")

    monkeypatch.setenv("USERS_DATA_PATH", str(users_path))
    monkeypatch.setenv(
        "AUTH_SECRET_KEY",
        "test-only-secret-1234567890-abcdefghijklmnopqrstuvwxyz"
    )

    from app.main import app

    with TestClient(app) as client:
        yield client

def test_login_page(login_client):
    response = login_client.get("/frontend/login.html")

    assert response.status_code == 200
    assert 'id="login-form"' in response.text
    assert 'src="/frontend/login.js"' in response.text
    assert 'src="/frontend/navbar.js"' in response.text

def test_login_javascript(login_client):
    response = login_client.get("/frontend/login.js")

    assert response.status_code == 200
    assert 'fetch("/auth/login"' in response.text
    assert 'sessionStorage.setItem("access_token"' in response.text

def test_navbar_login_logout(login_client):
    response = login_client.get("/frontend/navbar.js")

    assert response.status_code == 200

    js_code = response.text

    assert 'name: "Login", url: "/frontend/login.html", ready: true' in js_code
    assert 'sessionStorage.removeItem("access_token")' in js_code
    assert 'logoutButton.textContent = "Logout"' in js_code

def test_registration_then_login(login_client):
    customer = {
        "name": "Alex Customer",
        "email": "alex@example.com",
        "password": "secure-password-123"
    }

    response = login_client.post("/customers", json=customer)
    assert response.status_code == 201

    response = login_client.post("/auth/login", json={
        "email": customer["email"],
        "password": customer["password"]
    })

    assert response.status_code == 200

    token = response.json()["access_token"]

    response = login_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == customer["email"]
    assert response.json()["role"] == "customer"

    response = login_client.get("/auth/me")
    assert response.status_code == 401