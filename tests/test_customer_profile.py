import json

import pytest

from app.core.auth import create_access_token


PROFILE_URL = "/customers/me"
CHANGES = {"name": "Updated Customer", "delivery_address": "12 Main St"}
ADDRESS = {
    "street": " 24 Oak St, Unit 3 ",
    "city": "Vancouver",
    "region": "BC",
    "postal_code": "V6T 1Z4",
    "country": "Canada",
}


@pytest.fixture
def profile_client(client, tmp_path, monkeypatch):
    users = [
        {
            "id": user_id,
            "name": f"Account {user_id}",
            "email": f"account{user_id}@example.com",
            "role": role,
            "is_active": active,
            "delivery_address": None,
            "delivery_address_details": None,
            "password_hash": "stored-test-hash",
            "restaurant_ids": [],
        }
        for user_id, role, active in (
            (1, "customer", True),
            (2, "customer", True),
            (3, "restaurant owner", True),
            (4, "customer", False),
            (5, "admin", True),
        )
    ]
    users_path = tmp_path / "users.json"
    users_path.write_text(json.dumps(users), encoding="utf-8")
    monkeypatch.setenv("USERS_DATA_PATH", str(users_path))
    monkeypatch.setenv("AUTH_SECRET_KEY", "test-only-customer-profile-signing-secret")
    return client, users_path


def auth_headers(user_id):
    return {"Authorization": f"Bearer {create_access_token(user_id)}"}


def test_customer_can_retrieve_only_their_profile(profile_client):
    client, _ = profile_client
    response = client.get(PROFILE_URL, headers=auth_headers(1))

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Account 1",
        "email": "account1@example.com",
        "role": "customer",
        "is_active": True,
        "delivery_address": None,
        "delivery_address_details": None,
    }


def test_profile_update_persists_without_changing_other_accounts(profile_client):
    client, users_path = profile_client
    headers = auth_headers(1)
    other_headers = auth_headers(2)
    before = client.get(PROFILE_URL, headers=headers).json()
    other_before = client.get(PROFILE_URL, headers=other_headers).json()
    stored_before = json.loads(users_path.read_text(encoding="utf-8"))

    response = client.put(PROFILE_URL, json=CHANGES, headers=headers)

    assert response.status_code == 200
    expected = before | CHANGES
    assert response.json() == expected
    assert client.get(PROFILE_URL, headers=headers).json() == expected
    assert client.get(PROFILE_URL, headers=other_headers).json() == other_before
    stored = json.loads(users_path.read_text(encoding="utf-8"))
    assert stored == [stored_before[0] | CHANGES, *stored_before[1:]]

    response = client.put(PROFILE_URL, json=CHANGES | {"delivery_address": None}, headers=headers)
    assert response.status_code == 200
    assert client.get(PROFILE_URL, headers=headers).json()["delivery_address"] is None


def test_customer_can_add_update_and_retrieve_delivery_address(profile_client):
    client, users_path = profile_client
    headers = auth_headers(1)
    assert client.get(PROFILE_URL, headers=headers).json()["delivery_address"] is None

    response = client.put(PROFILE_URL, headers=headers, json=CHANGES | {"delivery_address": ADDRESS})
    assert response.status_code == 200
    assert response.json()["delivery_address"] == "24 Oak St, Unit 3, Vancouver, BC V6T 1Z4, Canada"
    assert response.json()["delivery_address_details"] == ADDRESS | {"street": "24 Oak St, Unit 3"}

    updated = ADDRESS | {"street": "56 Pine St"}
    response = client.put(PROFILE_URL, headers=headers, json=CHANGES | {"delivery_address": updated})
    assert response.status_code == 200
    assert client.get(PROFILE_URL, headers=headers).json() == response.json()
    assert client.get(PROFILE_URL, headers=auth_headers(2)).json()["delivery_address"] is None

    stored = json.loads(users_path.read_text(encoding="utf-8"))[0]
    assert stored["delivery_address"] == "56 Pine St, Vancouver, BC V6T 1Z4, Canada"
    assert stored["delivery_address_details"] == updated

    response = client.put(PROFILE_URL, headers=headers, json={"name": "New Name"})
    assert response.status_code == 200
    assert response.json()["delivery_address_details"] == updated


@pytest.mark.parametrize("field", ADDRESS)
def test_customer_address_rejects_missing_or_blank_required_fields(profile_client, field):
    client, users_path = profile_client
    headers = auth_headers(1)
    before = users_path.read_bytes()
    missing = {key: value for key, value in ADDRESS.items() if key != field}

    for address in (missing, ADDRESS | {field: "   "}):
        response = client.put(
            PROFILE_URL, headers=headers, json=CHANGES | {"delivery_address": address}
        )
        assert response.status_code == 422
        assert users_path.read_bytes() == before


@pytest.mark.parametrize("invalid_fields", [
    {"name": "  "},
    {"delivery_address": "  "},
    {"delivery_address": 123},
    {"id": 2},
    {"email": "new@example.com"},
    {"role": "admin"},
    {"is_active": False},
    {"password": "new-password"},
])
def test_invalid_or_protected_profile_fields_are_rejected(profile_client, invalid_fields):
    client, users_path = profile_client
    before = users_path.read_bytes()

    response = client.put(PROFILE_URL, json=CHANGES | invalid_fields, headers=auth_headers(1))

    assert response.status_code == 422
    assert users_path.read_bytes() == before


@pytest.mark.parametrize(("user_id", "status"), [(None, 401), (3, 403), (4, 401), (5, 403)])
def test_unauthorized_accounts_cannot_read_or_write_profile(profile_client, user_id, status):
    client, users_path = profile_client
    before = users_path.read_bytes()
    headers = auth_headers(user_id) if user_id is not None else {}

    assert client.get(PROFILE_URL, headers=headers).status_code == status
    assert client.put(PROFILE_URL, json=CHANGES, headers=headers).status_code == status
    assert users_path.read_bytes() == before


def test_customer_cannot_use_another_customers_id_in_profile_url(profile_client):
    client, users_path = profile_client
    before = users_path.read_bytes()
    headers = auth_headers(1)

    assert client.get("/customers/2", headers=headers).status_code == 404
    assert client.put("/customers/2", json=CHANGES, headers=headers).status_code == 404
    assert users_path.read_bytes() == before


def test_account_page_serves_form_and_script(client):
    response = client.get("/frontend/account.html")
    assert response.status_code == 200
    assert 'id="account-form"' in response.text
    assert 'id="email" type="email" readonly' in response.text
    assert 'src="/frontend/account.js"' in response.text

    script = client.get("/frontend/account.js")
    assert script.status_code == 200
    assert 'fetch("/customers/me"' in script.text
