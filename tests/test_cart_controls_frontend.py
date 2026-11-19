def test_cart_script_updates_quantities_through_the_cart_api(client):
    script = client.get("/frontend/cart.js").text
    assert 'changeCart("PUT", `/items/${line.menu_item_id}`' in script
    assert "Update quantity" in script
    assert "Quantity must be a whole number of 1 or more." in script


def test_cart_script_removes_items_through_the_cart_api(client):
    script = client.get("/frontend/cart.js").text
    assert 'changeCart("DELETE", `/items/${line.menu_item_id}`)' in script
    assert 'element("button", "Remove")' in script


def test_cart_script_clears_the_cart_after_confirmation(client):
    script = client.get("/frontend/cart.js").text
    assert 'changeCart("DELETE", "")' in script
    assert "window.confirm(" in script
    assert 'element("button", "Clear cart")' in script


def test_cart_script_redraws_backend_totals_after_every_change(client):
    script = client.get("/frontend/cart.js").text
    assert "renderCart(cart)" in script
    assert "cart.subtotal" in script and "cart.total" in script
    assert "error.message" in script
