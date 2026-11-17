
const navbar = document.getElementById("site-nav");

const pages = [
    { name: "Restaurants", url: "/", ready: true },
    { name: "Manage Restaurants", url: "/frontend/manage.html", ready: true },
    { name: "Login", url: "/frontend/login.html", ready: true },
    { name: "Register", url: "/frontend/register.html", ready: true },
    { name: "My Account", url: "/frontend/account.html", ready: false },
    { name: "Cart", url: "/frontend/cart.html", ready: false },
    { name: "Checkout", url: "/frontend/checkout.html", ready: false },
    { name: "Orders", url: "/frontend/orders.html", ready: false },
    { name: "Manage Menu", url: "/frontend/menu-management.html", ready: false },
    { name: "Reviews", url: "/frontend/reviews.html", ready: false }
];

async function showNavbar() {
    let currentUser = null;
    const token = sessionStorage.getItem("access_token");

    if (token) {
        try {
            const response = await fetch("/auth/me", {
                headers: {
                    "Authorization": "Bearer " + token
                }
            });

            if (response.ok) {
                currentUser = await response.json();
            } else if (response.status === 401) {
                sessionStorage.removeItem("access_token");
            }
        } catch (error) {
            console.error("Could not check login status:", error);
        }
    }

    const signedIn = currentUser !== null;

    const canManage = signedIn && (
        currentUser.role === "restaurant owner" ||
        currentUser.role === "admin"
    );

    for (const page of pages) {
        if (page.ready === false) {
            continue;
        }

        if (signedIn &&
            (page.name === "Login" || page.name === "Register")) {
            continue;
        }

        if (page.name === "Manage Restaurants" && !canManage) {
            continue;
        }

        const link = document.createElement("a");
        link.href = page.url;
        link.textContent = page.name;

        if (window.location.pathname === page.url) {
            link.className = "active";
            link.setAttribute("aria-current", "page");
        }

        navbar.appendChild(link);
    }

    if (signedIn) {
        const logoutButton = document.createElement("button");
        logoutButton.type = "button";
        logoutButton.textContent = "Logout";

        logoutButton.addEventListener("click", () => {
            sessionStorage.removeItem("access_token");
            window.location.href = "/";
        });

        navbar.appendChild(logoutButton);
    }
}

if (navbar) {
    showNavbar();
}