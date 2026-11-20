def test_cart_page_serves_cart_and_script(client):
    response = client.get("/frontend/cart.html")
    assert response.status_code == 200
    assert 'id="cart-items"' in response.text
    assert 'id="cart-summary"' in response.text
    assert 'src="/frontend/cart.js"' in response.text
    assert 'src="/frontend/navbar.js"' in response.text


def test_cart_script_shows_backend_totals_from_the_cart_api(client):
    script = client.get("/frontend/cart.js")
    assert script.status_code == 200
    assert "javascript" in script.headers["content-type"]
    assert "/cart" in script.text
    assert 'sessionStorage.getItem("access_token")' in script.text
    assert "cart.subtotal" in script.text and "cart.total" in script.text


def test_cart_link_is_in_the_customer_navigation(client):
    js_code = client.get("/frontend/navbar.js").text
    assert 'name: "Cart", url: "/frontend/cart.html", ready: true, roles: ["customer"]' in js_code




def test_cart_page_has_place_order_button(client):
    page = client.get("/frontend/cart.html").text
    assert 'id="place-order"' in page
    assert 'id="checkout-error"' in page


def test_place_order_button_calls_checkout_and_shows_the_order(client):
    script = client.get("/frontend/cart.js").text
    assert "/checkout`" in script and 'method: "POST"' in script
    assert "response.status === 201" in script
    assert "/frontend/orders.html?placed=" in script
    orders_script = client.get("/frontend/orders.js").text
    assert 'get("placed")' in orders_script
