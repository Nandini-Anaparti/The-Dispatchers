const cartStatus = document.getElementById("cart-status");
const cartError = document.getElementById("cart-error");
const cartLogin = document.getElementById("cart-login");
const cartContents = document.getElementById("cart-contents");
const cartItems = document.getElementById("cart-items");
const cartSummary = document.getElementById("cart-summary");

let customerId = null;
let authHeaders = null;

function money(amount) {
    return "$" + amount.toFixed(2);
}

function element(tag, text, className = "") {
    const node = document.createElement(tag);
    node.textContent = text;
    node.className = className;
    return node;
}

function showCartSignIn() {
    cartError.textContent = "Sign in to view your cart.";
    cartLogin.hidden = false;
}

function setBusy(busy) {
    for (const control of cartContents.querySelectorAll("button, input")) {
        control.disabled = busy;
    }
}

async function cartRequest(method, path, body) {
    const options = { method, headers: { ...authHeaders } };
    if (body) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(body);
    }

    const response = await fetch(`/customers/${customerId}/cart${path}`, options);
    if (response.status === 401) {
        sessionStorage.removeItem("access_token");
        showCartSignIn();
        return null;
    }
    if (!response.ok) {
        let message = "Could not update your cart. Please try again.";
        if (response.status === 403) {
            message = "You can only change your own cart.";
        } else {
            try {
                const data = await response.json();
                if (typeof data.detail === "string") {
                    message = data.detail;
                }
            } catch {
                // keep the default message
            }
        }
        throw new Error(message);
    }
    return response.json();
}

async function changeCart(method, path, body) {
    cartError.textContent = "";
    setBusy(true);
    try {
        const cart = await cartRequest(method, path, body);
        if (cart) {
            renderCart(cart);
        }
    } catch (error) {
        cartError.textContent = error.message;
    } finally {
        setBusy(false);
    }
}

function renderLine(line) {
    const card = document.createElement("article");
    card.className = "menu-card";

    const input = document.createElement("input");
    input.type = "number";
    input.min = "1";
    input.step = "1";
    input.value = line.quantity;
    input.id = "quantity-" + line.menu_item_id;

    const label = element("label", "Quantity");
    label.htmlFor = input.id;

    const update = element("button", "Update quantity");
    update.type = "button";
    update.addEventListener("click", () => {
        const quantity = Number(input.value);
        if (!Number.isInteger(quantity) || quantity < 1) {
            cartError.textContent = "Quantity must be a whole number of 1 or more.";
            input.focus();
            return;
        }
        changeCart("PUT", `/items/${line.menu_item_id}`, { quantity });
    });

    const remove = element("button", "Remove");
    remove.type = "button";
    remove.addEventListener("click", () => changeCart("DELETE", `/items/${line.menu_item_id}`));

    card.append(
        element("h3", line.name),
        element("p", `${money(line.unit_price)} each`),
        label,
        input,
        update,
        remove,
        element("p", "Line total " + money(line.line_total), "price")
    );
    return card;
}

function renderCart(cart) {
    cartItems.replaceChildren(...cart.items.map(renderLine));

    const summary = [
        element("p", "Subtotal " + money(cart.subtotal)),
        element("p", "Delivery fee " + money(cart.delivery_fee)),
        element("p", "Total " + money(cart.total), "price")
    ];
    if (cart.items.length > 0) {
        const clear = element("button", "Clear cart");
        clear.type = "button";
        clear.addEventListener("click", () => {
            if (window.confirm("Remove every item from your cart?")) {
                changeCart("DELETE", "");
            }
        });
        summary.push(clear);
    }
    cartSummary.replaceChildren(...summary);

    cartContents.hidden = cart.items.length === 0;
    cartStatus.textContent = cart.items.length === 0
        ? "Your cart is empty. Browse restaurants to add items."
        : "";
}

async function loadCart() {
    try {
        const token = sessionStorage.getItem("access_token");
        if (!token) {
            showCartSignIn();
            return;
        }

        authHeaders = { Authorization: "Bearer " + token };
        const session = await fetch("/auth/me", { headers: authHeaders });
        if (session.status === 401) {
            sessionStorage.removeItem("access_token");
            showCartSignIn();
            return;
        }
        if (!session.ok) {
            throw new Error("Session check failed");
        }
        const customer = await session.json();
        if (customer.role !== "customer") {
            cartError.textContent = "The cart is available to customer accounts.";
            return;
        }

        customerId = customer.id;
        const cart = await cartRequest("GET", "");
        if (cart) {
            renderCart(cart);
        }
    } catch {
        cartError.textContent = "Could not load your cart. Refresh to try again.";
    } finally {
        if (cartStatus.textContent === "Loading your cart…") {
            cartStatus.textContent = "";
        }
    }
}

loadCart();
