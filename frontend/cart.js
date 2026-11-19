const cartStatus = document.getElementById("cart-status");
const cartError = document.getElementById("cart-error");
const cartLogin = document.getElementById("cart-login");
const cartContents = document.getElementById("cart-contents");
const cartItems = document.getElementById("cart-items");
const cartSummary = document.getElementById("cart-summary");

function money(amount) {
    return "$" + amount.toFixed(2);
}

function element(tag, text, className = "") {
    const node = document.createElement(tag);
    node.textContent = text;
    node.className = className;
    return node;
}

function renderLine(line) {
    const card = document.createElement("article");
    card.className = "menu-card";
    card.append(
        element("h3", line.name),
        element("p", `${line.quantity} × ${money(line.unit_price)}`),
        element("p", money(line.line_total), "price")
    );
    return card;
}

function renderCart(cart) {
    cartItems.replaceChildren(...cart.items.map(renderLine));
    cartSummary.replaceChildren(
        element("p", "Subtotal " + money(cart.subtotal)),
        element("p", "Delivery fee " + money(cart.delivery_fee)),
        element("p", "Total " + money(cart.total), "price")
    );
    cartContents.hidden = cart.items.length === 0;
    cartStatus.textContent = cart.items.length === 0
        ? "Your cart is empty. Browse restaurants to add items."
        : "";
}

function showCartSignIn() {
    cartError.textContent = "Sign in to view your cart.";
    cartLogin.hidden = false;
}

async function loadCart() {
    try {
        const token = sessionStorage.getItem("access_token");
        if (!token) {
            showCartSignIn();
            return;
        }

        const headers = { Authorization: "Bearer " + token };
        const session = await fetch("/auth/me", { headers });
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

        const response = await fetch(`/customers/${customer.id}/cart`, { headers });
        if (response.status === 401) {
            sessionStorage.removeItem("access_token");
            showCartSignIn();
            return;
        }
        if (response.status === 403) {
            cartError.textContent = "You can only view your own cart.";
            return;
        }
        if (!response.ok) {
            throw new Error("Cart request failed");
        }

        renderCart(await response.json());
    } catch {
        cartError.textContent = "Could not load your cart. Refresh to try again.";
    } finally {
        if (cartStatus.textContent === "Loading your cart…") {
            cartStatus.textContent = "";
        }
    }
}

loadCart();
