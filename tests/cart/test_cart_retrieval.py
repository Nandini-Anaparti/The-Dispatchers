import json

from app.services.cart_service import CartService


def test_new_customer_gets_empty_active_cart(cart_client):
    body = cart_client.get("/customers/1/cart").json()
    assert body["customer_id"] == 1 and body["status"] == "active" and body["items"] == []


def test_existing_cart_is_retrieved_not_duplicated(cart_client, cart_env):
    first = cart_client.get("/customers/1/cart").json()
    second = cart_client.get("/customers/1/cart").json()
    assert first["id"] == second["id"]
    assert len(json.loads((cart_env.path / "carts.json").read_text())) == 1


def test_each_customer_gets_their_own_cart(cart_client):
    a = cart_client.get("/customers/1/cart").json()
    b = cart_client.get("/customers/3/cart").json()
    assert a["id"] != b["id"] and b["customer_id"] == 3


def test_cart_is_persisted_and_survives_a_restart(cart_env):
    def new_service():  # a brand-new service object, like after restarting the app
        return CartService(cart_env.cart_repo, cart_env.menu_repo,
                           cart_env.restaurant_repo, cart_env.user_repo)

    first = new_service().get_cart(1)
    assert new_service().get_cart(1).id == first.id
    saved = json.loads((cart_env.path / "carts.json").read_text())
    assert saved[0]["customer_id"] == 1


def test_deactivated_customer_cannot_get_cart(cart_client):
    assert cart_client.get("/customers/2/cart").status_code == 403


def test_unknown_customer_rejected(cart_client):
    assert cart_client.get("/customers/99/cart").status_code == 404

