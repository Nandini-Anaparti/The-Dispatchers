def test_add_to_cart_ignores_responses_after_the_customer_leaves_the_screen(client):
    script = client.get("/frontend/browsing.js").text
    assert "let cartMessageVersion = 0;" in script
    assert "const messageVersion = cartMessageVersion;" in script
    assert "messageVersion === cartMessageVersion" in script


def test_opening_or_leaving_a_restaurant_invalidates_pending_messages(client):
    script = client.get("/frontend/browsing.js").text
    # once when a restaurant is opened and once when the customer goes back
    assert script.count("cartMessageVersion += 1;") == 2


def test_session_expiry_still_signs_the_customer_out_when_the_message_is_skipped(client):
    script = client.get("/frontend/browsing.js").text
    assert 'sessionStorage.removeItem("access_token");\n      reportSignIn(' in script.replace("\r\n", "\n")
