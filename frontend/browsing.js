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
