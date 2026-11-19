def test_restaurant_page_script_adds_items_through_the_cart_api(client):
    script = client.get("/frontend/browsing.js")
    assert script.status_code == 200
    assert "javascript" in script.headers["content-type"]
    assert "/cart/items" in script.text
    assert 'method: "POST"' in script.text
    assert "menu_item_id: item.id" in script.text
    assert 'sessionStorage.getItem("access_token")' in script.text


def test_add_to_cart_button_is_only_offered_for_available_items(client):
    script = client.get("/frontend/browsing.js").text
    assert "if (item.is_available)" in script
    assert 'button.textContent = "Add to cart"' in script


def test_add_to_cart_shows_the_api_reason_and_a_cart_link(client):
    script = client.get("/frontend/browsing.js").text
    assert "response.status === 409" in script
    assert "data.detail" in script
    assert 'href: "/frontend/cart.html"' in script