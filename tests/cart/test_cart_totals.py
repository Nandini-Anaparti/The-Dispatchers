import json


def _seed(env, items, restaurant_id=1):
    cart = {"id": 1, "customer_id": 1, "restaurant_id": restaurant_id,
            "status": "active", "items": items}
    (env.path / "carts.json").write_text(json.dumps([cart]))


def test_empty_cart_totals_are_zero(signed_in_cart_client):
    body = signed_in_cart_client.get("/customers/1/cart").json()
    assert body["subtotal"] == 0 and body["delivery_fee"] == 0 and body["total"] == 0


def test_backend_calculates_subtotal_fee_and_total(signed_in_cart_client, cart_env):
    _seed(cart_env, [{"menu_item_id": 1, "quantity": 2}, {"menu_item_id": 2, "quantity": 1}])
    body = signed_in_cart_client.get("/customers/1/cart").json()
    assert body["subtotal"] == 25.0 and body["delivery_fee"] == 2.0 and body["total"] == 27.0


def test_lines_show_name_price_quantity_and_line_total(signed_in_cart_client, cart_env):
    _seed(cart_env, [{"menu_item_id": 1, "quantity": 3}])
    line = signed_in_cart_client.get("/customers/1/cart").json()["items"][0]
    assert line["name"] == "Item1" and line["unit_price"] == 10.0
    assert line["quantity"] == 3 and line["line_total"] == 30.0


def test_totals_use_current_menu_prices(signed_in_cart_client, cart_env):
    _seed(cart_env, [{"menu_item_id": 1, "quantity": 1}])
    menu = json.loads((cart_env.path / "menu.json").read_text())
    menu[0]["price"] = 12.5
    (cart_env.path / "menu.json").write_text(json.dumps(menu))
    assert signed_in_cart_client.get("/customers/1/cart").json()["subtotal"] == 12.5


def test_client_cannot_override_the_total(signed_in_cart_client, cart_env):
    _seed(cart_env, [{"menu_item_id": 1, "quantity": 1}])
    body = signed_in_cart_client.get("/customers/1/cart?total=0").json()
    assert body["total"] == 12.0  # 10 item + 2 delivery


def test_item_removed_from_menu_is_not_counted(signed_in_cart_client, cart_env):
    _seed(cart_env, [{"menu_item_id": 1, "quantity": 1}, {"menu_item_id": 2, "quantity": 1}])
    menu = [m for m in json.loads((cart_env.path / "menu.json").read_text()) if m["id"] != 1]
    (cart_env.path / "menu.json").write_text(json.dumps(menu))
    body = signed_in_cart_client.get("/customers/1/cart").json()
    assert len(body["items"]) == 1 and body["subtotal"] == 5.0
