# The Dispatchers

The Dispatchers is a food delivery application built using FastAPI for the backend and HTML, CSS, and JavaScript for the frontend.

The application includes restaurant and menu browsing, customer and restaurant owner registration, authentication, role-based access, restaurant and menu management, shopping carts, checkout validation, and order history. Data is stored in JSON files, and pytest is used for testing.

## Requirements

- Python 3.12
- Git
- Docker Desktop (optional, only needed if running the application in a container)

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Nandini-Anaparti/The-Dispatchers.git
cd The-Dispatchers
```

The `main` branch contains the latest integrated version of the application. You do not need to switch branches to run it.

### 2. Create and Activate a Virtual Environment

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Windows (Command Prompt):

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### 3. Install Dependencies

From the project root, with the virtual environment active:

```bash
python -m pip install -r requirements.txt
```

### 4. Set the Authentication Secret Key

The application uses JWT tokens for authentication. Before starting the backend, set the `AUTH_SECRET_KEY` environment variable.

Windows (PowerShell):

```powershell
$env:AUTH_SECRET_KEY = python -c "import secrets; print(secrets.token_urlsafe(32))"
```

macOS / Linux:

```bash
export AUTH_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
```

Run this command in the same terminal where you will start the application. The secret key is used to sign and verify authentication tokens.

Do not commit the secret key or any other authentication credentials to GitHub.

## Running the Application

### Option A: Local (Virtual Environment)

From the project root, with the virtual environment active and `AUTH_SECRET_KEY` set:

```bash
python -m uvicorn app.main:app --reload
```

The application runs at http://127.0.0.1:8000.

Open the following links in your browser:

- Frontend: http://127.0.0.1:8000/
- API documentation: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

The health check should return:

```json
{
  "status": "ok"
}
```

Stop the application using `Ctrl+C`.

### Option B: Docker

Make sure Docker Desktop is running.

From the project root, with `AUTH_SECRET_KEY` already set in your terminal:

```bash
docker compose build
docker compose run --rm --service-ports -e AUTH_SECRET_KEY api
```

The application runs at http://localhost:8000.

The `-e AUTH_SECRET_KEY` option passes the authentication secret from your terminal into the container.

Stop the application using `Ctrl+C`. You can then run:

```bash
docker compose down
```

## Frontend - Milestone 1

The application includes a restaurant-browsing frontend built with HTML, CSS, and JavaScript.

Once the application is running, open http://127.0.0.1:8000/ in your browser.

The frontend supports:

- Viewing restaurants retrieved from the REST API.
- Searching restaurants by name and filtering by cuisine.
- Viewing a selected restaurant's details.
- Viewing menu items, prices, and availability.
- Loading, empty-result, and error messages.

Search and cuisine filtering currently run in the browser using restaurant data retrieved from the API.

The main frontend files are located in `frontend/`: `index.html`, `styles.css`, and `browsing.js`.

`GET /` serves the frontend page. API documentation is available at `/docs`.

Tests in `tests/test_frontend.py` verify that the page and static assets are served correctly and that missing assets return 404. These tests do not execute browser interactions.

## Milestone 2 - User Accounts and Menu Management

### Registration and Login

Users can register as either customers or restaurant owners.

- Customers can register through `/frontend/register.html`.
- Restaurant owners can register through `/frontend/owner-register.html`.
- Registration checks for duplicate email addresses and invalid information.
- Passwords are hashed before being saved.
- Registered users can log in through `/frontend/login.html`.

The backend uses JWT tokens for authentication. After a successful login, the frontend saves the access token in `sessionStorage` and includes it when making requests to protected endpoints.

The `/auth/me` endpoint is used to check the signed-in user's information. Logging out removes the saved token.

### Role-Based Access and Navigation

The application supports three user roles: customer, restaurant owner, and admin.

The navigation bar displays links based on the user's role:

- Guests can browse restaurants and access Login and Register.
- Customers can access their account, cart, and orders.
- Restaurant owners can access Manage Restaurants and Manage Menu.
- Admins can manage restaurants and menus.

Links to unfinished pages are kept hidden until those pages are implemented.

The backend also checks user permissions, so hiding a link in the frontend is not the only restriction.

Protected endpoints return HTTP 401 for missing or invalid authentication and HTTP 403 when an authenticated user does not have the required permissions.

### Restaurant and Menu Management

Restaurant owners can create restaurants and manage the ones assigned to their accounts. Admins can manage all restaurants.

After logging in, restaurant owners and admins can use `/frontend/manage.html` to create or update restaurant information.

They can also use `/frontend/menu-management.html` to:

- View menu items for restaurants they are allowed to manage.
- Add new menu items.
- Update item names, descriptions, prices, and availability.
- Deactivate menu items that are no longer offered.

Deactivated menu items are kept in JSON storage but hidden from public menus. Restaurant owners and admins can still view them through the management page. Items that are temporarily unavailable remain visible to customers but are marked as unavailable.

Menu changes are saved through the existing FastAPI routes, services, repositories, and JSON storage.

### Trying the Application

Once the backend is running, open http://127.0.0.1:8000/.

#### As a Customer

1. Select Register and create a customer account.
2. Log in using the email and password you registered with.
3. Browse the available restaurants and select one to view its menu.
4. Add an available menu item to your cart.
5. Select Cart from the navigation bar to view your items and the total calculated by the backend.
6. Select My Account to view or update your account information and delivery address.

For a quick example, you can select La Vela Pizzeria from the existing restaurant data. Its menu includes Margherita Pizza and Garlic Bread.

The Orders page displays orders saved for the signed-in customer. New accounts will have an empty order history until an order has been created.

#### As a Restaurant Owner

1. Open Register and select Register as a Restaurant Owner.
2. Create an account and log in.
3. Select Manage Restaurants to create a restaurant or update one assigned to your account.
4. Select Manage Menu to add or update menu items.
5. Change an item's availability or deactivate an item.
6. Check that the updated information is saved and displayed correctly.

Restaurant owners can only manage their assigned restaurants. Admins can manage all restaurants.

## API Endpoints

The API does not use a common `/api` prefix. For example, restaurant information is available at `/restaurants`.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check. Returns `200` and `{"status": "ok"}` |
| GET | `/restaurants` | Returns all restaurants. Optional filters: `name` (partial, case-insensitive), `cuisine`, `is_open`, `min_rating` (0 to 5, otherwise `422`) |
| GET | `/restaurants/{restaurant_id}` | Returns one restaurant, or `404` if it does not exist |
| POST | `/restaurants` | Creates a restaurant with a server-assigned ID. Requires restaurant owner or admin access. Returns `201`, or `422` for invalid input |
| PUT | `/restaurants/{restaurant_id}` | Updates only the fields provided. Requires permission to manage the restaurant. Returns `404` for an unknown ID, or `422` for invalid input |
| GET | `/restaurants/mine` | Returns the restaurants assigned to a restaurant owner, or all restaurants for an admin |
| POST | `/customers` | Registers a customer account |
| POST | `/restaurant-owners` | Registers a restaurant owner account |
| POST | `/auth/login` | Verifies login credentials and returns an access token |
| GET | `/auth/me` | Returns the authenticated user's information |
| GET | `/customers/me` | Returns the signed-in customer's profile |
| PUT | `/customers/me` | Updates the customer's name or delivery address |
| POST | `/customers/me/deactivate` | Deactivates the signed-in customer account |
| GET | `/customers/{customer_id}/orders` | Returns the signed-in customer's orders, newest first. Requires access to that customer's account |
| GET | `/customers/{customer_id}/orders/{order_id}` | Returns an order belonging to the signed-in customer, or `404` if it does not exist or is not theirs |
| POST | `/customers/{customer_id}/checkout` | Places an order from the active cart. Revalidates items, recalculates totals, saves the order, then closes the cart. Returns `201`, or `409` if the cart is empty or an item is unavailable |
| POST | `/customers/{customer_id}/orders/{order_id}/cancel` | Cancels the customer's order while its status is `placed`. Returns `409` otherwise |
| GET | `/restaurants/{restaurant_id}/orders` | Returns the restaurant's orders, newest first. Requires the restaurant owner or admin |
| PATCH | `/restaurants/{restaurant_id}/orders/{order_id}/status` | Moves an order to its next status. Returns `409` if the change is not allowed |
| GET | `/docs` | Interactive OpenAPI (Swagger) documentation |

The restaurant list supports the following optional filters:

- `name`: Partial, case-insensitive match.
- `cuisine`: Case-insensitive match.
- `is_open`: Filter by open or closed restaurants.
- `min_rating`: Minimum rating from 0 to 5. Invalid values return HTTP 422.

For example:

```text
http://127.0.0.1:8000/restaurants?cuisine=italian&is_open=true
```

### Authentication

To access protected endpoints, first log in through the frontend or send a request to `POST /auth/login`.

Example request body:

```json
{
  "email": "your-email@example.com",
  "password": "your-password"
}
```

Use the email and password of an account you registered.

The response includes an `access_token`. Send the token with protected API requests using:

```text
Authorization: Bearer <access_token>
```

You can also open `/docs`, use the login endpoint to obtain a token, and enter it through the Authorize option in Swagger.

Authentication tokens expire after one hour. If a token expires, log in again to obtain a new one.

### Customer Profile

Sign in as a customer and select My Account in the navigation.

Customers can update their name and delivery address. The account email is read-only.

To add or change an address, select Add or edit address, enter the required information, and save the changes. Select Remove saved address to remove it.

For API requests:

| Endpoint | Successful response |
|----------|---------------------|
| `GET /customers/me` | `200 OK` with the signed-in customer's profile |
| `PUT /customers/me` | `200 OK` with the updated profile |

The profile update requires `name`. A structured `delivery_address` must include `street`, `city`, `region`, `postal_code`, and `country`.

Omitting `delivery_address` keeps the current address. Sending `null` removes it.

Existing single-string addresses remain supported. Responses do not include passwords, password hashes, or tokens.

The API returns:

- `401` for missing or invalid authentication, or an inactive account.
- `403` when the authenticated user does not have customer access.
- `422` for invalid input.

Customers can also deactivate their accounts through My Account.

`POST /customers/me/deactivate` returns `204 No Content` and marks the account inactive. Existing customer and order records are retained.

Run the customer profile tests using:

```bash
python -m pytest tests/test_customer_profile.py -v
```

### Menu API

All paths below are relative to `/restaurants/{restaurant_id}/menu-items`.

| Method | Path suffix | Access | Operation |
|--------|-------------|--------|-----------|
| `GET` | Base path | Public | List active menu items. Optional filters are `name`, `max_price`, and `is_available`. |
| `GET` | `/{item_id}` | Public | Get an active menu item. |
| `GET` | `/manage` | Menu management | List menu items, including deactivated items. |
| `POST` | Base path | Menu management | Create a menu item. |
| `PUT` | `/{item_id}` | Menu management | Update a menu item. |
| `PATCH` | `/{item_id}/deactivate` | Menu management | Deactivate a menu item. |

Menu management requires an `Authorization: Bearer <access_token>` header.

Restaurant owners can manage their assigned restaurants, and admins can manage any restaurant. Public menu browsing does not require authentication.

#### HTTP Status Codes

| Code | Meaning for the Menu API |
|------|-------------------------|
| `200 OK` | The API returned menu data, updated an item, or deactivated an item. |
| `201 Created` | A new menu item was created. |
| `401 Unauthorized` | Authentication is missing, invalid, or expired. |
| `403 Forbidden` | The user does not have permission to manage the restaurant. |
| `404 Not Found` | The restaurant or menu item does not exist, or the item belongs to another restaurant. |
| `422 Unprocessable Content` | The request contains invalid information, such as a zero or negative price. |

#### Request Examples

Browse restaurant `1` without credentials:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/restaurants/1/menu-items'
```

To create a menu item, first log in as a restaurant owner or admin and obtain an access token.

Use a restaurant ID that your account has permission to manage.

```powershell
$headers = @{ Authorization = 'Bearer <access_token>' }

$item = @{
    name = 'Tomato Pasta'
    description = 'Pasta with tomato sauce'
    price = 12.99
    is_available = $true
} | ConvertTo-Json

Invoke-RestMethod 'http://127.0.0.1:8000/restaurants/1/menu-items' `
    -Method Post -Headers $headers -ContentType 'application/json' -Body $item
```

Replace `<access_token>` with the token returned by the login endpoint.

Run the authorization tests using:

```bash
python -m pytest tests/test_role_auth.py -v
```

### Shopping Cart

Shopping cart operations require a signed-in customer. Customers can only access their own carts.

The backend supports:

| Method | Path | Operation |
|--------|------|-----------|
| GET | `/customers/{customer_id}/cart` | Retrieve or create an active cart and return its contents and totals |
| POST | `/customers/{customer_id}/cart/items` | Add an available menu item to the cart |
| PUT | `/customers/{customer_id}/cart/items/{menu_item_id}` | Update the quantity of an item |
| DELETE | `/customers/{customer_id}/cart/items/{menu_item_id}` | Remove an item |
| DELETE | `/customers/{customer_id}/cart` | Clear the cart |

Cart items must belong to the same restaurant. The backend also checks that items exist, are active, and are available before adding them.

The cart stores menu item IDs and quantities. Prices and totals are calculated by the backend using current menu information.

### Checkout Validation

`POST /customers/{customer_id}/checkout/validate` requires the customer's bearer token.

It checks the current customer, active cart, restaurant status, menu item availability, quantities, and required business rules.

An absent active cart returns `404`. An empty or invalid cart, closed or missing restaurant, or unavailable menu item returns `409`.

Checkout validation does not modify the saved cart or orders.

### Placing an Order

`POST /customers/{customer_id}/checkout` places an order. It repeats the validation and pricing checks, saves the order through the Order Repository, and only then closes the cart. A failed checkout leaves the cart unchanged.

A successful checkout returns `201` with the new order. The Cart page's **Place order** button calls this endpoint and opens the Orders page after the order is placed.

Run the end-to-end test using:

```bash
python -m pytest tests/orders/test_customer_to_order_workflow.py -v
```

### Checkout Pricing

`POST /customers/{customer_id}/checkout/price` performs the same checks as checkout validation and recalculates the subtotal, delivery fee, and total using current menu prices.

If a menu item's price has changed since it was added to the cart, checkout uses the updated price.

Totals supplied by the client are ignored. This endpoint does not save an order or close the cart.

The cart and checkout use the same calculation in `app/services/pricing.py`, so they return consistent totals.

Run the pricing tests using:

```bash
python -m pytest tests/cart/test_checkout_pricing.py -v
```

### Order Creation and Order History

The order service contains functionality to create and save an order from a validated, priced cart.

It saves the order before closing the cart. If saving the order fails, the cart is left unchanged.

Saved orders contain the purchased items, quantities, prices, totals, customer and restaurant IDs, and order status.

Customers can retrieve their own saved orders through:

| Method | Path | Operation |
|--------|------|-----------|
| GET | `/customers/{customer_id}/orders` | Retrieve order history, newest first |
| GET | `/customers/{customer_id}/orders/{order_id}` | Retrieve an individual order |

Sign in as a customer and select Orders to view saved orders.

The order history uses prices saved when the order was created, so later menu changes do not change previous orders.

The checkout finalization logic currently exists in the service layer. The API endpoint and frontend needed to place an order are not yet connected on `main`.

Run the order tests using:

```bash
python -m pytest tests/orders/ -v
```

## Data and Configuration

The application uses JSON files for persistence.

| File | Purpose |
|------|---------|
| `data/restaurants.json` | Restaurant information |
| `data/menu_items.json` | Menu items and availability |
| `data/users.json` | Registered users and account information |
| `data/carts.json` | Shopping carts |
| `data/orders.json` | Saved orders |

Each restaurant has a stable integer `id`, `name`, `cuisine`, `rating`, `delivery_time_minutes`, `delivery_fee`, `address`, and `is_open`.

Data file paths can be changed using environment variables:

| Environment Variable | Default File |
|----------------------|--------------|
| `RESTAURANTS_DATA_PATH` | `data/restaurants.json` |
| `MENU_ITEMS_DATA_PATH` | `data/menu_items.json` |
| `USERS_DATA_PATH` | `data/users.json` |
| `CARTS_DATA_PATH` | `data/carts.json` |
| `ORDERS_DATA_PATH` | `data/orders.json` |

If these variables are not set, the application uses the default JSON files relative to the project root.

This also allows tests to use temporary data files without changing the committed application data.

The repository includes sample restaurant and menu information. New customers and restaurant owners can be registered through the frontend.

## Architecture

The application follows a layered structure:

```text
Frontend
   |
   v
FastAPI Routes
   |
   v
Service Layer
   |
   v
Repository Layer
   |
   v
JSON Storage
```

Each layer has a separate responsibility:

- Frontend: Displays information and sends requests to the API.
- Routes: Handle HTTP requests, status codes, authentication dependencies, and response models.
- Services: Handle application logic, validation, and business rules.
- Repositories: Read and write data.
- JSON: Stores application data.

For example, a restaurant request follows:

```text
HTTP Request
  -> Route       app/api/routes/restaurants.py
  -> Service     app/services/restaurant_service.py
  -> Repository  app/repositories/restaurant_repository.py
  -> JSON        data/restaurants.json
```

Routes do not directly read the JSON files. The Pydantic models in `app/schemas/` define the data used by the API.

The same structure is used for customer accounts, menu management, carts, checkout, and orders.

### Milestone 2 Architectural Improvement

The menu service originally had the same restaurant existence check repeated in three functions: `get_menu_items()`, `get_menu_item()`, and `add_menu_item()`.

PR #135 introduces a shared `require_restaurant()` function in `MenuItemService`. The three functions use this shared check instead of repeating the same validation.

Regression tests were added to check that requests involving nonexistent restaurants still return HTTP 404 without changing the stored menu data.

An integration test was also added to check that deactivating a menu item prevents it from being added to a cart and causes checkout validation to reject an existing cart containing that item.

The improvement and supporting tests are documented in PR #135 and the M2.1 Decision Receipt.

## Running Tests

From the project root, with the virtual environment active:

```bash
python -m pytest
```

Add `-v` to see each test by name.

You do not need to start Uvicorn before running the tests. FastAPI's `TestClient` sends requests directly to the application during testing.

On Windows PowerShell, you can also run tests without activating the virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

### Milestone 0 and 1 Tests

The original tests cover the health endpoint, restaurant endpoints, menu operations, repository behaviour, and failure cases.

| Requirement | Test File |
|-------------|-----------|
| Health endpoint | `tests/test_health.py` |
| Restaurant list | `tests/test_restaurants_api.py` |
| Restaurant lookup and missing IDs | `tests/test_restaurant_by_id.py` |
| Restaurant repository and invalid data | `tests/test_restaurant_repository.py` |
| Menu browsing and management | `tests/test_menu_items.py` |

The original restaurant tests use pytest fixtures to create temporary data.

The `sample_restaurants` fixture in `tests/conftest.py` provides test restaurants, while `temp_data_file` writes them into a temporary directory.

The `client` fixture uses `monkeypatch` to set `RESTAURANTS_DATA_PATH` to the temporary file. Pytest restores the original environment variable after the test.

### Milestone 2 Tests

Additional tests cover customer and restaurant owner registration, authentication, login and logout, role-based authorization, navigation, menu management, cart operations, checkout validation, pricing, and orders.

Tests include successful operations, invalid inputs, authentication failures, permission checks, persistence, and cross-subsystem behaviour.

To run the main M2 tests for registration, authentication, authorization, navigation, and menu management:

```bash
python -m pytest tests/test_customer_registration.py tests/test_restaurant_owner_registration.py tests/test_auth.py tests/test_login_frontend.py tests/test_role_auth.py tests/test_navbar.py tests/test_menu_items.py tests/test_menu_management_frontend.py -v
```

To run the cart and checkout tests:

```bash
python -m pytest tests/cart/ -v
```

To run the order tests:

```bash
python -m pytest tests/orders/ -v
```

To run the full test suite:

```bash
python -m pytest -v
```

### Regression and Integration Testing

Regression tests were added after integration and refactoring to make sure existing behaviour continued working.

The menu service regression tests verify that requests involving nonexistent restaurants still return HTTP 404 and do not modify the stored menu data.

An integration test in `tests/cart/test_checkout_validation.py` checks the interaction between menu management, cart, and checkout.

It verifies that:

1. A customer can add an available menu item to their cart.
2. An authorized user can deactivate that item.
3. The deactivated item no longer appears in public menu browsing.
4. The customer cannot add that item to the cart again.
5. Checkout validation rejects the existing cart containing the deactivated item.
6. Failed validation does not change the saved cart or order data.

Tests use temporary or isolated JSON data to avoid changing the representative application data.

### Continuous Integration

GitHub Actions runs the automated pytest suite when changes are pushed to `main` or when a pull request targets `main`.

The workflow is defined in `.github/workflows/python-app.yml`.

To check the results:

1. Open the repository on GitHub.
2. Select the Actions tab.
3. Open the Python application workflow.
4. Select a workflow run to see whether the tests passed or failed.

The workflow currently uses Python 3.10. The local setup and Docker image use Python 3.12.

## Repository Structure

```text
The-Dispatchers/
├── app/
│   ├── api/
│   │   └── routes/          # API endpoints
│   ├── core/                # Configuration, authentication, permissions
│   ├── repositories/        # JSON data access and persistence
│   ├── schemas/             # Pydantic request and response models
│   ├── services/            # Business logic and validation
│   └── main.py              # FastAPI application and router setup
├── frontend/                # HTML, CSS, and JavaScript
├── data/                    # JSON data files
├── tests/
│   ├── cart/                # Cart and checkout tests
│   ├── orders/              # Order tests
│   └── ...                  # Other API and frontend tests
├── docs/
│   └── PROVENANCE.md        # AI usage documentation
├── scrum/                   # Team agreement and scrum records
├── .github/
│   └── workflows/
│       └── python-app.yml   # Automated pytest workflow
├── Dockerfile
├── compose.yaml
├── requirements.txt
└── README.md
```

## Notes

- Authentication and role-based authorization were added in Milestone 2.
- Set `AUTH_SECRET_KEY` before starting the application or using authenticated endpoints.
- User passwords are stored as hashes, not plain text.
- Do not commit passwords, authentication tokens, API keys, or `.env` files containing secrets.
- The application uses JSON storage rather than a database.
- The full customer-to-order workflow requires the remaining checkout API and frontend integration before it can be demonstrated end to end.