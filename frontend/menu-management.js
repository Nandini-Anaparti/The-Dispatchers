const $ = id => document.getElementById(id);

let restaurantId = null;
let menuItemId = null;
let menuItems = [];

function showError(message) {
    $("error").textContent = message;
    $("success").textContent = "";
}

function showSuccess(message) {
    $("success").textContent = message;
    $("error").textContent = "";
}

async function api(method, path, body) {
    const token = sessionStorage.getItem("access_token");

    const options = {
        method: method,
        headers: {
            "Authorization": "Bearer " + token
        }
    };

    if (body) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(body);
    }

    const response = await fetch(path, options);

    if (!response.ok) {
        let message = "Request failed (" + response.status + ")";

        if (response.status === 401) {
            message = "Your login has expired. Please log in again.";
        } else if (response.status === 403) {
            message = "You do not have permission to manage this restaurant.";
        } else {
            try {
                const data = await response.json();

                if (typeof data.detail === "string") {
                    message = data.detail;
                } else if (Array.isArray(data.detail)) {
                    message = data.detail.map(
                        error => error.msg
                    ).join("; ");
                }
            } catch (error) {
                console.error(error);
            }
        }

        throw new Error(message);
    }

    return response.json();
}

function resetForm() {
    menuItemId = null;
    $("menu-item-form").reset();

    $("item-name").disabled = false;
    $("item-description").disabled = false;
    $("item-price").disabled = false;
    $("item-available").disabled = false;

    $("item-submit").hidden = false;
    $("item-submit").textContent = "Add Menu Item";
    $("deactivate-item").hidden = true;
}

function fillForm(item) {
    if (!item) {
        resetForm();
        return;
    }

    menuItemId = item.id;

    $("item-name").value = item.name;
    $("item-description").value = item.description;
    $("item-price").value = item.price;
    $("item-available").checked = item.is_available;

    const inactive = !item.is_active;

    $("item-name").disabled = inactive;
    $("item-description").disabled = inactive;
    $("item-price").disabled = inactive;
    $("item-available").disabled = inactive;

    $("item-submit").hidden = inactive;
    $("item-submit").textContent = "Update Menu Item";

    $("deactivate-item").hidden = inactive;
}
function showMenuList() {
    const list = $("menu-list");
    list.replaceChildren();

    menuItems.forEach(item => {
        const entry = document.createElement("li");

        let status = "Available";

        if (!item.is_active) {
            status = "Deactivated";
        } else if (!item.is_available) {
            status = "Unavailable";
        }

        entry.textContent =
            item.name + " - $" + item.price.toFixed(2) +
            " (" + status + ")";

        list.appendChild(entry);
    });
}

async function loadMenuItems(selectedId = null) {
    menuItems = await api(
        "GET",
        "/restaurants/" + restaurantId + "/menu-items/manage"
    );

    const select = $("menu-item-select");

    select.replaceChildren(
        new Option("-- New menu item --", "")
    );

    menuItems.forEach(item => {
        select.add(new Option(
            item.id + ": " + item.name,
            item.id
        ));
    });

    showMenuList();

    $("menu-status").textContent = menuItems.length === 0
        ? "No menu items yet. Add your first item below."
        : menuItems.length + " menu item(s) found.";

    const selectedItem = menuItems.find(
        item => item.id === selectedId
    );

    if (selectedItem) {
        select.value = String(selectedItem.id);
        fillForm(selectedItem);
    } else {
        select.value = "";
        resetForm();
    }
}

async function selectRestaurant(id) {
    restaurantId = id ? Number(id) : null;
    menuItems = [];
    resetForm();

    $("error").textContent = "";
    $("success").textContent = "";

    $("menu-section").hidden = !restaurantId;

    if (!restaurantId) {
        return;
    }

    try {
        await loadMenuItems();
    } catch (error) {
        showError(error.message);
        $("menu-section").hidden = true;
    }
}

$("restaurant-select").addEventListener("change", event => {
    selectRestaurant(event.target.value);
});

$("menu-item-select").addEventListener("change", event => {
    const selectedId = event.target.value
        ? Number(event.target.value)
        : null;

    const selectedItem = menuItems.find(
        item => item.id === selectedId
    );

    fillForm(selectedItem);

    $("error").textContent = "";
    $("success").textContent = "";
});

$("menu-item-form").addEventListener("submit", async event => {
    event.preventDefault();

    const price = Number($("item-price").value);

    if (price <= 0 || !Number.isFinite(price)) {
        showError("Price must be greater than $0.");
        return;
    }

    const body = {
        name: $("item-name").value.trim(),
        description: $("item-description").value.trim(),
        price: price,
        is_available: $("item-available").checked
    };

    const path = "/restaurants/" + restaurantId + "/menu-items";

    try {
        const saved = menuItemId
            ? await api("PUT", path + "/" + menuItemId, body)
            : await api("POST", path, body);

        await loadMenuItems(saved.id);

        showSuccess('Saved "' + saved.name + '".');

    } catch (error) {
        showError(error.message);
    }
});

$("deactivate-item").addEventListener("click", async () => {
    if (!restaurantId || !menuItemId) {
        return;
    }

    const item = menuItems.find(
        item => item.id === menuItemId
    );

    if (!item || !item.is_active) {
        return;
    }

    const confirmed = window.confirm(
        'Deactivate "' + item.name + '"? ' +
        "Customers will no longer see this item."
    );

    if (!confirmed) {
        return;
    }

    const path =
        "/restaurants/" + restaurantId +
        "/menu-items/" + menuItemId +
        "/deactivate";

    try {
        await api("PATCH", path);

        await loadMenuItems(item.id);

        showSuccess(
            '"' + item.name + '" has been deactivated.'
        );

    } catch (error) {
        showError(error.message);
    }
});

async function checkAccess() {
    const token = sessionStorage.getItem("access_token");

    if (!token) {
        $("access-message").textContent =
            "Please log in as a restaurant owner or admin.";
        return;
    }

    try {
        const response = await fetch("/auth/me", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        if (response.status === 401) {
            sessionStorage.removeItem("access_token");

            $("access-message").textContent =
                "Your login has expired. Please log in again.";
            return;
        }

        if (!response.ok) {
            throw new Error("Could not check your account.");
        }

        const user = await response.json();

        if (user.role !== "restaurant owner" &&
            user.role !== "admin") {
            $("access-message").textContent =
                "You do not have permission to manage menus.";
            return;
        }

        // Load only restaurants this user can manage.
        const restaurants = await api("GET", "/restaurants/mine");

        $("access-message").hidden = true;
        $("menu-content").hidden = false;

        const select = $("restaurant-select");

        restaurants.forEach(restaurant => {
            select.add(new Option(
                restaurant.id + ": " + restaurant.name,
                restaurant.id
            ));
        });

        if (restaurants.length === 0) {
            $("restaurant-message").textContent =
                "You have no restaurants yet. Create one first.";
            return;
        }

        // Check whether a restaurant was passed in the URL.
        const params = new URLSearchParams(window.location.search);
        const requestedId = Number(params.get("restaurant_id"));

        const selectedRestaurant = restaurants.find(
            restaurant => restaurant.id === requestedId
        ) || restaurants[0];

        select.value = String(selectedRestaurant.id);
        await selectRestaurant(selectedRestaurant.id);

    } catch (error) {
        $("access-message").hidden = false;
        $("access-message").textContent = error.message;
        $("menu-content").hidden = true;
        console.error(error);
    }
}

checkAccess();