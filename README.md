# The Dispatchers

Food delivery application with a FastAPI backend. This README covers the Milestone 0 (M0) backend foundation: a health check, a restaurant list endpoint, JSON persistence, and a pytest test suite.

## Requirements

- Python 3.12
- Git
- Docker Desktop (optional, only needed if you want to run the app in a container)

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Nandini-Anaparti/The-Dispatchers.git
cd The-Dispatchers
```

To run the exact version submitted for M0:

```bash
git checkout foundation-gate
```

### 2. Create and activate a virtual environment

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

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

### Option A: Local (virtual environment)

From the project root, with the virtual environment active:

```bash
python -m uvicorn app.main:app --reload
```

The API runs at http://127.0.0.1:8000.

### Option B: Docker

From the project root:

```bash
docker compose up --build
```

The API runs at http://localhost:8000. Stop it with `Ctrl+C`, then `docker compose down`.

## Frontend — Milestone 1

The application includes a basic restaurant-browsing frontend built with
HTML, CSS, and JavaScript.

Start the application:

```bash
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/ in your browser.

The frontend supports:

- Viewing restaurants retrieved from the REST API.
- Searching restaurants by name and filtering by cuisine.
- Viewing a selected restaurant's details.
- Viewing its menu items, prices, and availability.
- Loading, empty-result, and error messages.

Search and cuisine filtering currently run in the browser using restaurant data retrieved from the API.

Frontend files are located in `frontend/`: `index.html`, `styles.css`, and `browsing.js`.

`GET /` now serves the frontend page instead of the original JSON welcome message. API documentation remains available at `/docs`.

Tests in `tests/test_frontend.py` verify that the page and static assets are served correctly and missing assets return 404. These tests do not execute browser interactions.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check. Returns `200` and `{"status": "ok"}` |
| GET | `/restaurants` | Returns all restaurants. Optional filters: `name` (partial, case-insensitive), `cuisine`, `is_open`, `min_rating` (0 to 5, otherwise `422`) |
| GET | `/restaurants/{restaurant_id}` | Returns one restaurant, or `404` if the id does not exist |
| POST | `/restaurants` | Creates a restaurant (server assigns the id). Returns `201`, or `422` if the body is invalid |
| PUT | `/restaurants/{restaurant_id}` | Updates only the fields sent. Returns `404` if the id does not exist, or `422` if a field is invalid |
| GET | `/customers/{customer_id}/orders` | Your order history, newest first (customer token, own account only) |
| GET | `/customers/{customer_id}/orders/{order_id}` | One of your orders. `404` if it does not exist or is not yours |
| GET | `/restaurants/{restaurant_id}/orders` | That restaurant's orders, newest first. Owner of that restaurant or admin |
| PATCH | `/restaurants/{restaurant_id}/orders/{order_id}/status` | Move an order to its next status. `409` if the move is not allowed |
| GET | `/docs` | Interactive OpenAPI (Swagger) documentation |

Example filter: `/restaurants?cuisine=italian&is_open=true` returns open Italian restaurants.

No API prefix is used. For example, the restaurant list is at http://127.0.0.1:8000/restaurants and the docs are at http://127.0.0.1:8000/docs.

### Customer Order History

Sign in as a customer and select **Orders** in the navigation. Your newest orders appear first. Expand **View order items** to see quantities, the prices saved when the order was placed, and the delivery fee. Order history uses the saved order snapshot, so later menu edits have no effect on past orders.

Run the order retrieval tests with `python -m pytest tests/orders/test_order_retrieval.py -v`.

### Customer Profile

Set `AUTH_SECRET_KEY` in the backend process environment before starting the app. Sign in as a customer and select **My Account** in the navigation. To enter or change your delivery address, select **Add or edit address**, fill in the required fields, and select **Save changes**. Choose **Remove saved address** to clear it. Your sign-in email is read-only.

For API requests, obtain an access token from `POST /auth/login` and send it in the `Authorization: Bearer <access_token>` header. Both profile endpoints use the account identified by the token.

| Endpoint | Successful response |
|----------|---------------------|
| `GET /customers/me` | `200 OK` with the signed-in customer's profile |
| `PUT /customers/me` | `200 OK` with the updated profile after saving it to JSON |

The update body requires `name`. To save a structured `delivery_address`, include `street`, `city`, `region`, `postal_code`, and `country`. Omit `delivery_address` to keep the current address or send `null` to remove it. Responses include the formatted address and its structured details when available. Existing single-string addresses remain supported. Responses exclude passwords, password hashes, and tokens.

The API returns `401` for missing or invalid authentication or an inactive account, `403` for an authenticated account with a role other than customer, and `422` for invalid values or fields outside the update contract.

To deactivate an account, select **Deactivate my account** in **My Account** and confirm. The app signs the customer out. `POST /customers/me/deactivate` returns `204 No Content` and marks the account inactive. Existing customer and order records are retained.

User records are stored in `data/users.json` by default. Set `USERS_DATA_PATH` to use a different JSON file. Run the profile tests from the project root with the virtual environment active.

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

Menu management requires an `Authorization: Bearer <access_token>` header. Restaurant owners can manage their assigned restaurants, and admins can manage any restaurant. Customers can use the public endpoints.

#### HTTP status codes

| Code | Meaning for the Menu API |
|------|-------------------------|
| `200 OK` | The API returned the requested menu data, updated an item, or deactivated an item. |
| `201 Created` | The API created a menu item and returned it. |
| `401 Unauthorized` | The protected endpoint received a missing, invalid, or expired bearer token. |
| `403 Forbidden` | The user authenticated successfully but lacks permission to manage the restaurant. |
| `404 Not Found` | The restaurant or item could not be found. This also applies when the item belongs to a different restaurant than the one in the URL. |
| `422 Unprocessable Content` | The request failed validation, for example because the item price was zero or negative. |

#### Request examples

Browse restaurant `1` without credentials.

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/restaurants/1/menu-items'
```

For local authentication, set `AUTH_SECRET_KEY` in the environment that runs the backend before starting it. Send the account's email and password to `POST /auth/login` and copy the `access_token` from the response. Use a restaurant ID your account can manage when creating an item.

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

Run the role authorization tests from the project root with the virtual environment active.

```bash
python -m pytest tests/test_role_auth.py -q
```

### Checkout validation

`POST /customers/{customer_id}/checkout/validate` requires the customer's bearer token and returns the active cart if it is ready for pricing. It checks the account, cart contents, restaurant status, item availability, and quantities against current data. Validation leaves the cart and orders unchanged.

An absent active cart returns `404`. An empty or invalid cart, closed or missing restaurant, or unavailable item returns `409`.

## Data and Configuration

Representative restaurant data is stored in:

```
data/restaurants.json
```

Each restaurant has a stable integer `id`, `name`, `cuisine`, `rating`, `delivery_time_minutes`, `delivery_fee`, `address`, and `is_open`.

The data file location is configurable through the `RESTAURANTS_DATA_PATH` environment variable. If it is not set, the app uses `data/restaurants.json` relative to the project root. No machine-specific paths are hard-coded. The test suite uses this variable to point the app at temporary test data, so running the tests never modifies the committed data file.

## Architecture

Each restaurant request passes through four layers, each with one responsibility:

```
HTTP Request
  -> Route       app/api/routes/restaurants.py              (HTTP concerns: paths, status codes, response models)
  -> Service     app/services/restaurant_service.py         (application and business logic)
  -> Repository  app/repositories/restaurant_repository.py  (reads and validates stored data)
  -> JSON        data/restaurants.json                       (persistence)
```

Routes never read the JSON file directly. The `Restaurant` Pydantic model in `app/schemas/restaurant.py` defines the data contract and is used as the endpoint's `response_model`.

## Running Tests

From the project root, with the virtual environment active:

```bash
python -m pytest
```

Add `-v` to see each test by name. The tests cover the health endpoint, the restaurant endpoints (including a missing restaurant returning `404`), repository behaviour, and failure cases such as a missing or invalid data file. All tests use temporary data created with pytest's `tmp_path`.

On Windows PowerShell, you can also run tests without activating the environment:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

You do not need to start Uvicorn: FastAPI's `TestClient` runs requests inside
the test process.

The test setup works as follows:

1. `sample_restaurants` in `tests/conftest.py` supplies two fictional restaurants.
2. `temp_data_file` writes them to a separate `tmp_path` directory for each test.
3. `client` uses `monkeypatch` to set `RESTAURANTS_DATA_PATH` to that file.
   Pytest restores the environment variable after each test.
4. Tests send requests or call the repository and use `assert` to check results.
   Failure tests use `pytest.raises` to check expected exceptions.

The tests cover all four required areas:

| Requirement | What was checked |
|-------------|------------------|
| Health endpoint | `/health` returns `200` and `{"status": "ok"}`. |
| Restaurant-list operation | `/restaurants` returns the expected restaurants and handles an empty list. |
| Restaurant data/repository behavior | Reads correct records, looks up IDs, and leaves the data file unchanged. |
| Meaningful invalid or failure case | Missing files, malformed JSON, missing required fields, unknown IDs (`404`), and non-integer IDs (`422`). |

The corresponding test files are:

| Requirement | Tests |
|-------------|-------|
| Health endpoint status and JSON | `tests/test_health.py` |
| Restaurant list contents and empty list | `tests/test_restaurants_api.py` |
| Repository reads, lookups, and unchanged file contents | `tests/test_restaurant_repository.py` |
| Missing file, malformed JSON, invalid structure | `tests/test_restaurant_repository.py` |
| Unknown restaurant (404), non-integer ID (422) | `tests/test_restaurant_by_id.py` |

The suite does not read or modify `data/restaurants.json`; all data checks use
temporary fixtures.

<!-- TODO: Continuous Integration section. Describe the GitHub Actions workflow (file location, when it runs, how to see results). -->

## Repository Structure

```
The-Dispatchers/
├── app/
│   ├── api/routes/restaurants.py        # Restaurant endpoints
│   ├── core/config.py                   # Configuration (data file path)
│   ├── repositories/restaurant_repository.py
│   ├── schemas/restaurant.py            # Pydantic models
│   ├── services/restaurant_service.py
│   └── main.py                          # FastAPI app, /health, router setup
├── data/
│   └── restaurants.json                 # Representative restaurant data
├── tests/                               # pytest test suite
├── scrum/
│   └── team-agreement.md                # Team agreement (versioned weekly)
├── Dockerfile
├── compose.yaml
├── requirements.txt
└── README.md
```

## Notes

- Authentication is planned for later milestones and is not part of M0.
- This repository contains no passwords, tokens, or API keys. Do not commit secrets or `.env` files.
