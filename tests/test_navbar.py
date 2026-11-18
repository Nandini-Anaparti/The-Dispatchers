import pytest

@pytest.mark.parametrize("page", ["/", "/frontend/manage.html", "/frontend/orders.html"])
def test_navbar_on_pages(client, page):
    response = client.get(page)

    assert response.status_code == 200
    assert 'id="site-nav"' in response.text
    assert 'src="/frontend/navbar.js"' in response.text

def test_navbar_js_loads(client):
    response = client.get("/frontend/navbar.js")

    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]

def test_navbar_css(client):
    response = client.get("/frontend/styles.css")

    assert response.status_code == 200
    assert "#site-nav" in response.text
    assert "#site-nav a" in response.text
    assert "#site-nav a.active" in response.text

def test_navbar_links(client):
    response = client.get("/frontend/navbar.js")

    assert response.status_code == 200

    js_code = response.text

    assert 'name: "Restaurants", url: "/", ready: true' in js_code
    assert 'name: "Manage Restaurants", url: "/frontend/manage.html", ready: true' in js_code

def test_unfinished_pages(client):
    response = client.get("/frontend/navbar.js")

    assert response.status_code == 200

    js_code = response.text

    assert 'name: "Cart", url: "/frontend/cart.html", ready: false' in js_code

def test_role_based_navigation(client):
    response = client.get("/frontend/navbar.js")

    assert response.status_code == 200

    js_code = response.text

    assert 'fetch("/auth/me"' in js_code
    assert "currentUser = await response.json()" in js_code
    assert "page.roles.includes(role)" in js_code
    assert 'name: "Orders", url: "/frontend/orders.html", ready: true, roles: ["customer"]' in js_code

    assert (
        'name: "Manage Restaurants", url: "/frontend/manage.html", '
        'ready: true, roles: ["restaurant owner", "admin"]'
    ) in js_code

    assert (
        'name: "Manage Menu", url: "/frontend/menu-management.html", '
        'ready: true, roles: ["restaurant owner", "admin"]'
    ) in js_code

    assert (
        'name: "My Account", url: "/frontend/account.html", '
        'ready: false, roles: ["customer"]'
    ) in js_code

    assert (
        'name: "Login", url: "/frontend/login.html", '
        'ready: true, roles: ["guest"]'
    ) in js_code

    assert 'logoutButton.textContent = "Logout"' in js_code
    assert 'sessionStorage.removeItem("access_token")' in js_code
