const orderHistory = document.getElementById("order-history");
const orderHistoryStatus = document.getElementById("order-history-status");
const orderHistoryError = document.getElementById("order-history-error");
const orderHistoryLogin = document.getElementById("order-history-login");
const orderDateFormat = new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short"
});

function orderMoney(amount) {
    return "$" + amount.toFixed(2);
}

function orderElement(tag, text) {
    const element = document.createElement(tag);
    element.textContent = text;
    return element;
}

function renderOrder(order) {
    const card = document.createElement("article");
    card.className = "restaurant-card";
    const date = orderElement("time", orderDateFormat.format(new Date(order.created_at)));
    date.dateTime = order.created_at;
    const status = order.status[0].toUpperCase() + order.status.slice(1);
    const total = orderElement("p", "Total " + orderMoney(order.total));
    total.className = "price";

    const details = document.createElement("details");
    const items = document.createElement("ul");
    for (const item of order.items) {
        items.append(orderElement(
            "li",
            `${item.quantity} × ${item.name} at ${orderMoney(item.unit_price)} each — ${orderMoney(item.line_total)}`
        ));
    }
    details.append(
        orderElement("summary", "View order items"),
        items,
        orderElement("p", "Subtotal " + orderMoney(order.subtotal)),
        orderElement("p", "Delivery fee " + orderMoney(order.delivery_fee))
    );
    card.append(orderElement("h2", "Order #" + order.id), date,
        orderElement("p", "Restaurant #" + order.restaurant_id),
        orderElement("p", status), total, details);
    return card;
}

function showOrderSignIn() {
    orderHistoryError.textContent = "Sign in to view your orders.";
    orderHistoryLogin.hidden = false;
}

async function loadOrderHistory() {
    try {
        const token = sessionStorage.getItem("access_token");
        if (!token) {
            showOrderSignIn();
            return;
        }

        const headers = { Authorization: "Bearer " + token };
        const session = await fetch("/auth/me", { headers });
        if (session.status === 401) {
            sessionStorage.removeItem("access_token");
            showOrderSignIn();
            return;
        }
        if (!session.ok) {
            throw new Error("Session check failed");
        }
        const customer = await session.json();
        if (customer.role !== "customer") {
            orderHistoryError.textContent = "Order history is available to customer accounts.";
            return;
        }

        const response = await fetch(`/customers/${customer.id}/orders`, { headers });
        if (response.status === 401) {
            sessionStorage.removeItem("access_token");
            showOrderSignIn();
            return;
        }
        if (response.status === 403) {
            orderHistoryError.textContent = "You can only view your own orders.";
            return;
        }
        if (!response.ok) {
            throw new Error("Order history request failed");
        }

        const orders = await response.json();
        orderHistory.replaceChildren(...orders.map(renderOrder));
        if (orders.length === 0) {
            orderHistoryStatus.textContent = "You haven't placed any orders yet.";
            return;
        }
        const placedId = new URLSearchParams(window.location.search).get("placed");
        if (placedId) {
            orderHistoryStatus.textContent = `Order #${placedId} placed! You can see it below.`;
        }
    } catch {
        orderHistoryError.textContent = "Could not load your orders. Refresh to try again.";
    } finally {
        if (orderHistoryStatus.textContent === "Loading your orders…") {
            orderHistoryStatus.textContent = "";
        }
    }
}

loadOrderHistory();
