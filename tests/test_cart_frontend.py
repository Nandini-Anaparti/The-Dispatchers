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


