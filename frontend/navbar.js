const navbar = document.getElementById("site-nav");

const pages = [
    { name: "Restaurants", url: "/", ready: true },
    { name: "Manage Restaurants", url: "/frontend/manage.html", ready: true },
    { name: "Login", url: "/frontend/login.html", ready: false },
    { name: "Register", url: "/frontend/register.html", ready: false },
    { name: "My Account", url: "/frontend/account.html", ready: false },
    { name: "Cart", url: "/frontend/cart.html", ready: false },
    { name: "Checkout", url: "/frontend/checkout.html", ready: false },
    { name: "Orders", url: "/frontend/orders.html", ready: false },
    { name: "Manage Menu", url: "/frontend/menu-management.html", ready: false },
    { name: "Reviews", url: "/frontend/reviews.html", ready: false }
];

if (navbar) {
    for (const page of pages) {

        if (page.ready === false) {
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
}