
const navbar = document.getElementById("site-nav");

const pages = [
    { name: "Restaurants", url: "/", ready: true, roles: ["guest", "customer", "restaurant owner", "admin"] },
    { name: "Manage Restaurants", url: "/frontend/manage.html", ready: true, roles: ["restaurant owner", "admin"] },
    { name: "Manage Menu", url: "/frontend/menu-management.html", ready: true, roles: ["restaurant owner", "admin"] },
    { name: "Login", url: "/frontend/login.html", ready: true, roles: ["guest"] },
    { name: "Register", url: "/frontend/register.html", ready: true, roles: ["guest"] },
    { name: "My Account", url: "/frontend/account.html", ready: false, roles: ["customer"] },
    { name: "Cart", url: "/frontend/cart.html", ready: false, roles: ["customer"] },
    { name: "Checkout", url: "/frontend/checkout.html", ready: false, roles: ["customer"] },
    { name: "Orders", url: "/frontend/orders.html", ready: true, roles: ["customer"] },
    { name: "Reviews", url: "/frontend/reviews.html", ready: false, roles: ["customer"] }
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

    const role = currentUser ? currentUser.role : "guest";

    navbar.replaceChildren();

    for (const page of pages) {
        if (!page.ready) {
            continue;
        }

        if (!page.roles.includes(role)) {
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

    if (currentUser) {
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
