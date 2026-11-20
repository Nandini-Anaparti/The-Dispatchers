const restaurantList = document.querySelector("#restaurant-list");
const restaurantStatus = document.querySelector("#restaurant-status");
const menuHeading = document.querySelector("#menu-heading");
const searchForm = document.querySelector("#search-form");
const searchInput = document.querySelector("#search");
const cuisineSelect = document.querySelector("#cuisine");

let allRestaurants = [];

function createRestaurantCard(restaurant) {
  const card = document.createElement("article");
  card.className = "restaurant-card";

  const name = document.createElement("h3");
  name.textContent = restaurant.name;

  const cuisine = document.createElement("p");
  cuisine.textContent = restaurant.cuisine;

  const rating = document.createElement("p");
  rating.textContent = `Rating: ${restaurant.rating} / 5`;

  const delivery = document.createElement("p");
  delivery.textContent =
    `${restaurant.delivery_time_minutes} min · ` +
    `$${restaurant.delivery_fee.toFixed(2)} delivery`;

  const availability = document.createElement("p");
  availability.className = restaurant.is_open
    ? "availability"
    : "availability unavailable";
  availability.textContent = restaurant.is_open ? "Open" : "Closed";
  
  const button = document.createElement("button");
  button.type = "button";
  button.dataset.restaurantId = restaurant.id;
  button.textContent = "View restaurant";
  button.addEventListener("click", () => {
  showRestaurant(restaurant.id);
});

  card.append(name, cuisine, rating, delivery, availability, button);
  return card;
}

function displayRestaurants() {
  const search = searchInput.value.trim().toLowerCase();
  const cuisine = cuisineSelect.value;
  const matches = allRestaurants.filter((restaurant) => {
    const matchesName = restaurant.name.toLowerCase().includes(search);
    const matchesCuisine = !cuisine || restaurant.cuisine === cuisine;
    return matchesName && matchesCuisine;
  });

  restaurantList.replaceChildren();
  matches.forEach((restaurant) => {
    restaurantList.append(createRestaurantCard(restaurant));
  });

  restaurantStatus.classList.remove("error");
  restaurantStatus.textContent = allRestaurants.length === 0
    ? "No restaurants are available yet."
    : matches.length
      ? `${matches.length} restaurants found.`
      : "No restaurants match your search. Try another name or cuisine.";
}

async function loadRestaurants() {
  searchInput.disabled = true;
  cuisineSelect.disabled = true;
  searchForm.querySelector('button[type="submit"]').disabled = true;
  restaurantStatus.classList.remove("error");
  restaurantStatus.textContent = "Loading restaurants…";
  restaurantList.replaceChildren();

  try {
    const response = await fetch("/restaurants");

    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }

    allRestaurants = await response.json();
    cuisineSelect.replaceChildren(new Option("All cuisines", ""));
    const cuisines = [...new Set(
      allRestaurants.map((restaurant) => restaurant.cuisine)
    )].sort();
    cuisines.forEach((cuisine) => {
      cuisineSelect.add(new Option(cuisine, cuisine));
    });

    displayRestaurants();
    searchInput.disabled = false;
    cuisineSelect.disabled = false;
    searchForm.querySelector('button[type="submit"]').disabled = false;
  } catch (error) {
    restaurantStatus.classList.add("error");
    restaurantStatus.textContent =
      "Could not load restaurants. Please refresh the page to try again.";
    console.error(error);
  }
}

const detailsSection = document.querySelector("#restaurant-details");
const detailsHeading = document.querySelector("#details-heading");
const detailsStatus = document.querySelector("#details-status");
const restaurantInfo = document.querySelector("#restaurant-info");
const menuList = document.querySelector("#menu-list");
const backButton = document.querySelector("#back-button");

// Shows the result of adding an item to the cart, right under the loading status.
const cartMessage = document.createElement("p");
cartMessage.id = "cart-message";
cartMessage.setAttribute("role", "status");
detailsStatus.after(cartMessage);

// Counts how many restaurant screens the customer has opened or left. An Add to cart
// response only shows its message if this number is unchanged since the request started.
let cartMessageVersion = 0;

const browsingSections = [
  document.querySelector("#search-form").closest("section"),
  document.querySelector("#restaurant-list").closest("section"),
];

let activeRequest = null;
let selectedRestaurantId = null;

async function fetchJson(url, signal) {
  const response = await fetch(url, { signal });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}

function addText(parent, tag, text, className = "") {
  const element = document.createElement(tag);
  element.textContent = text;
  element.className = className;
  parent.append(element);
  return element;
}

function showCartMessage(text, isError = false, link = null) {
  cartMessage.replaceChildren(text);
  cartMessage.classList.toggle("error", isError);
  if (link) {
    const anchor = document.createElement("a");
    anchor.href = link.href;
    anchor.textContent = link.label;
    cartMessage.append(" ", anchor);
  }
}

function showCartSignIn(text) {
  showCartMessage(text, true, { href: "/frontend/login.html", label: "Sign in" });
}

async function addToCart(item, button) {
  const token = sessionStorage.getItem("access_token");
  if (!token) {
    showCartSignIn("Sign in as a customer to add items to your cart.");
    return;
  }

  // Messages from this request only appear while the customer is still on the same screen.
  const messageVersion = cartMessageVersion;
  const report = (text, isError = false, link = null) => {
    if (messageVersion === cartMessageVersion) {
      showCartMessage(text, isError, link);
    }
  };
  const reportSignIn = (text) => report(text, true, { href: "/frontend/login.html", label: "Sign in" });

  button.disabled = true;
  report("Adding to your cart…");
  try {
    const headers = { Authorization: "Bearer " + token };
    const session = await fetch("/auth/me", { headers });
    if (session.status === 401) {
      sessionStorage.removeItem("access_token");
      reportSignIn("Your session has expired. Sign in again to add items.");
      return;
    }
    if (!session.ok) {
      throw new Error(`Request failed: ${session.status}`);
    }
    const customer = await session.json();
    if (customer.role !== "customer") {
      report("Only customer accounts can add items to a cart.", true);
      return;
    }

    const response = await fetch(`/customers/${customer.id}/cart/items`, {
      method: "POST",
      headers: { ...headers, "Content-Type": "application/json" },
      body: JSON.stringify({ menu_item_id: item.id, quantity: 1 }),
    });
    if (response.status === 401) {
      sessionStorage.removeItem("access_token");
      reportSignIn("Your session has expired. Sign in again to add items.");
      return;
    }
    if (response.status === 404 || response.status === 409) {
      const data = await response.json();
      const reason = typeof data.detail === "string" ? data.detail : "That item could not be added.";
      report(reason, true);
      return;
    }
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }

    report(`Added "${item.name}" to your cart.`, false, {
      href: "/frontend/cart.html",
      label: "View cart",
    });
  } catch (error) {
    report("Could not add the item. Please try again.", true);
    console.error(error);
  } finally {
    button.disabled = false;
  }
}

function createMenuCard(item) {
  const card = document.createElement("article");
  card.className = "menu-card";

  addText(card, "h4", item.name);
  addText(card, "p", item.description);
  addText(card, "p", `$${item.price.toFixed(2)}`, "price");
  addText(
    card,
    "p",
    item.is_available ? "Available" : "Unavailable",
    item.is_available ? "availability" : "availability unavailable"
  );

  if (item.is_available) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = "Add to cart";
    button.addEventListener("click", () => addToCart(item, button));
    card.append(button);
  }

  return card;
}

async function showRestaurant(id) {
  activeRequest?.abort();
  const controller = new AbortController();
  activeRequest = controller;
  selectedRestaurantId = id;

  browsingSections.forEach((section) => {
    section.hidden = true;
  });

  detailsSection.hidden = false;
  detailsHeading.textContent = "Restaurant details";
  detailsHeading.focus();
  detailsStatus.classList.remove("error");
  detailsStatus.textContent = "Loading restaurant and menu…";
  cartMessageVersion += 1;
  cartMessage.replaceChildren();
  restaurantInfo.replaceChildren();
  restaurantInfo.className = "";
  menuList.replaceChildren();

  menuHeading.hidden = true;

  try {
    const restaurant = await fetchJson(
      `/restaurants/${id}`,
      controller.signal
    );

    detailsHeading.textContent = restaurant.name;
    restaurantInfo.className = "restaurant-info";

    addText(restaurantInfo, "p", restaurant.cuisine);
    addText(restaurantInfo, "p", restaurant.address);
    addText(
      restaurantInfo,
      "p",
      `Rating: ${restaurant.rating} / 5`
    );
    addText(
      restaurantInfo,
      "p",
      `${restaurant.delivery_time_minutes} min · ` +
        `$${restaurant.delivery_fee.toFixed(2)} delivery`
    );
    addText(
      restaurantInfo,
      "p",
      restaurant.is_open ? "Open" : "Closed",
      restaurant.is_open ? "availability" : "availability unavailable"
    );

    detailsStatus.textContent = "Loading menu…";

    const items = await fetchJson(
      `/restaurants/${id}/menu-items`,
      controller.signal
    );

    menuHeading.hidden = items.length === 0;

    items.forEach((item) => {
      menuList.append(createMenuCard(item));
    });

    detailsStatus.textContent = items.length
      ? `${items.length} menu items found.`
      : "This restaurant has no menu items yet.";
  } catch (error) {
    if (error.name === "AbortError") return;

    detailsStatus.classList.add("error");
    detailsStatus.textContent =
      "Could not load the restaurant or menu. Go back and try again.";
    console.error(error);
  }
}

backButton.addEventListener("click", () => {
  activeRequest?.abort();
  cartMessageVersion += 1;
  cartMessage.replaceChildren();
  detailsSection.hidden = true;

  browsingSections.forEach((section) => {
    section.hidden = false;
  });

  const buttons = restaurantList.querySelectorAll("button");
  const selectedButton = [...buttons].find(
    (button) => button.dataset.restaurantId === String(selectedRestaurantId)
  );

  selectedButton?.focus();
});

searchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  if (!searchInput.disabled) displayRestaurants();
});

cuisineSelect.addEventListener("change", displayRestaurants);

loadRestaurants();
