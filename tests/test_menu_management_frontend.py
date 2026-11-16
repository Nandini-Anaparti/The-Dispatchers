def test_menu_management_page(client):
    response = client.get("/frontend/menu-management.html")

    assert response.status_code == 200
    assert 'id="menu-item-form"' in response.text
    assert 'id="restaurant-select"' in response.text
    assert 'id="menu-item-select"' in response.text
    assert 'src="/frontend/menu-management.js"' in response.text

    response = client.get("/frontend/menu-management.js")

    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]

    response = client.get("/frontend/manage.html")

    assert response.status_code == 200
    assert 'id="manage-menu-link"' in response.text