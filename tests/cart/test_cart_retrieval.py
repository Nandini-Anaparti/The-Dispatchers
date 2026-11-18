import json
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

from app.services.cart_service import CartService


def test_new_customer_gets_empty_active_cart(cart_client, cart_auth_headers):
    response = cart_client.get("/customers/1/cart", headers=cart_auth_headers(1))
    assert response.status_code == 200
    body = response.json()
    assert body["customer_id"] == 1 and body["status"] == "active" and body["items"] == []


def test_existing_cart_is_retrieved_not_duplicated(cart_client, cart_env, cart_auth_headers):
    headers = cart_auth_headers(1)
    first = cart_client.get("/customers/1/cart", headers=headers).json()
    second = cart_client.get("/customers/1/cart", headers=headers).json()
    assert first["id"] == second["id"]
    assert len(json.loads((cart_env.path / "carts.json").read_text())) == 1


def test_each_customer_gets_their_own_cart(cart_client, cart_auth_headers):
    a = cart_client.get("/customers/1/cart", headers=cart_auth_headers(1)).json()
    b = cart_client.get("/customers/3/cart", headers=cart_auth_headers(3)).json()
    assert a["id"] != b["id"] and b["customer_id"] == 3


def test_cart_is_persisted_and_survives_a_restart(cart_env):
    def new_service():  # a brand-new service object, like after restarting the app
        return CartService(cart_env.cart_repo, cart_env.menu_repo,
                           cart_env.restaurant_repo, cart_env.user_repo)

    first = new_service().get_cart(1)
    assert new_service().get_cart(1).id == first.id
    saved = json.loads((cart_env.path / "carts.json").read_text())
    assert saved[0]["customer_id"] == 1


@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer invalid-token"}])
def test_cart_requires_valid_authentication(cart_client, cart_env, headers):
    response = cart_client.get("/customers/1/cart", headers=headers)
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert cart_env.cart_repo.get_all() == []


def test_deactivated_customer_cannot_get_cart(cart_client, cart_env, cart_auth_headers):
    response = cart_client.get("/customers/2/cart", headers=cart_auth_headers(2))
    assert response.status_code == 401
    assert cart_env.cart_repo.get_all() == []


def test_customer_cannot_access_another_customers_cart(cart_client, cart_env, cart_auth_headers):
    headers = cart_auth_headers(1)
    assert cart_client.get("/customers/3/cart", headers=headers).status_code == 403
    assert cart_env.cart_repo.get_all() == []

    cart_client.get("/customers/3/cart", headers=cart_auth_headers(3)).raise_for_status()
    before = cart_env.cart_repo.get_all()
    assert cart_client.get("/customers/3/cart", headers=headers).status_code == 403
    assert cart_env.cart_repo.get_all() == before


def test_unknown_customer_cannot_authenticate(cart_client, cart_auth_headers):
    response = cart_client.get("/customers/99/cart", headers=cart_auth_headers(99))
    assert response.status_code == 401


def test_noncustomer_cannot_create_cart(cart_client, cart_env, cart_auth_headers):
    response = cart_client.get("/customers/4/cart", headers=cart_auth_headers(4))
    assert response.status_code == 403
    assert cart_env.cart_repo.get_all() == []


def test_concurrent_requests_return_one_active_cart(cart_client, cart_env, cart_auth_headers):
    headers = cart_auth_headers(1)
    ready = Barrier(2, timeout=5)

    def request_cart():
        ready.wait()
        response = cart_client.get("/customers/1/cart", headers=headers)
        assert response.status_code == 200
        return response.json()

    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(request_cart)
        second = executor.submit(request_cart)

    carts = cart_env.cart_repo.get_all()
    assert len(carts) == 1
    assert carts[0].status == "active"
    assert first.result()["id"] == second.result()["id"] == carts[0].id
