# AI Provenance

This file records how generative AI was used to produce or influence work in this project, following the course's Generative AI Use and Provenance Guide.

Each entry uses one label: **AI-GENERATED**, **AI-ASSISTED**, **AI-REVISED**, or **NO-AI**.

Each team member adds their own entries under their name. A single artifact can have more than one entry if more than one person used AI on it.

## Entry template

Copy this block for each new entry.

```
### Entry N
- Student(s):
- Artifact:
- Label:
- AI tool:
- Purpose:
- Influence:
- Validation:
- PR:
```

---

## Ayah Hamdona

### Milestone 2 (Integrated Core System)

#### Entry AY1
- Student(s): Ayah Hamdona
- Artifact: `app/services/customer_rules.py`, `app/schemas/cart.py`, `app/repositories/cart_repository.py`, `app/services/cart_service.py`, `app/api/routes/carts.py`, `tests/cart/`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: CART-01 to CART-06: create or retrieve the active cart, add items, update quantities, remove items, clear the cart, and calculate totals in the backend, plus the shared active-customer rule used by the cart and checkout.
- Influence: Used the generated implementation and tests, and followed its step-by-step instructions to split the work into one pull request per user story.
- Validation: Ran the full pytest suite locally before each pull request, including tests for the one-active-cart rule, one restaurant per cart, unavailable items, invalid quantities, totals that follow current menu prices, deactivated customers, and persistence to JSON. Teammates reviewed each pull request. Domenica later added ownership checks and atomic repository updates on top of this work.
- PR: [#101](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/101), [#102](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/102), [#104](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/104), [#105](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/105), [#106](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/106), [#108](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/108)

#### Entry AY2
- Student(s): Ayah Hamdona
- Artifact: `app/services/pricing.py`, `app/services/cart_service.py` (`build_view`), `app/services/checkout_service.py` (`price`), `app/api/routes/checkout.py` (`POST /customers/{customer_id}/checkout/price`), `tests/cart/test_checkout_pricing.py`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: CHECKOUT-02: recalculate the subtotal, delivery fee, and total from current menu prices at checkout, and move the price calculation that the cart and checkout both need into one function.
- Influence: Used the generated implementation and tests.
- Validation: Ran the full pytest suite locally (267 passing), including tests that a menu price change before checkout changes the total, that the cart file stores no prices, that totals sent by a client are ignored, and that the cart view and checkout always show the same totals. The existing cart totals tests still pass unchanged after the refactor.
- PR: [#129](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/129)

---

## Anjana Ratnala

### Milestone 0 (Foundation Gate)

#### Entry A1
- Student(s): Anjana Ratnala
- Artifact: `app/core/config.py`, `app/schemas/restaurant.py`, `app/repositories/restaurant_repository.py`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Implement the restaurant data layer (configurable data path, `Restaurant` Pydantic model, JSON repository).
- Influence: Used the generated implementation.
- Validation: Ran the full pytest suite locally, including the existing repository tests, and confirmed all tests passed before opening the PR. Reviewed the code and explained it to the TA during the M0 lab demo.
- PR: [#1](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/1) (restored by [#9](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/9))

#### Entry A2
- Student(s): Anjana Ratnala
- Artifact: `app/services/restaurant_service.py`, `app/api/routes/restaurants.py`, `app/main.py`, `tests/test_restaurant_by_id.py`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Implement the restaurant service and routes (`GET /restaurants`, `GET /restaurants/{id}` with 404 handling) and tests for the by-id endpoint.
- Influence: Used the generated implementation and tests.
- Validation: Ran the full pytest suite locally, including tests that an unknown restaurant id returns 404, and confirmed all tests passed before opening the PR. Reviewed the code and explained it to the TA during the M0 lab demo.
- PR: [#2](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/2)

#### Entry A3
- Student(s): Anjana Ratnala
- Artifact: `README.md`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Write the README (setup, endpoints, tests, project structure).
- Influence: Used the generated documentation.
- Validation: Checked that the documented endpoints, commands and file paths match the actual code and project structure.
- PR: [#3](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/3)

### Milestone 1 (First Vertical Slice)

#### Entry A4
- Student(s): Anjana Ratnala
- Artifact: `app/services/restaurant_service.py`, `app/api/routes/restaurants.py`, `tests/test_restaurant_search.py`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Implement restaurant search and filter on `GET /restaurants` (name, cuisine, is_open, min_rating) and its tests.
- Influence: Used the generated implementation and tests.
- Validation: Ran the full pytest suite locally (35 passing), including tests for each filter, combined filters, no matches, and an invalid `min_rating` returning 422. Manually tested the filters through the FastAPI `/docs` page in the running app, and reviewed the implementation by walking through the code and explaining how each layer works.
- PR: [#15](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/15)

#### Entry A5
- Student(s): Anjana Ratnala
- Artifact: `app/schemas/restaurant.py`, `app/repositories/restaurant_repository.py`, `app/services/restaurant_service.py`, `app/api/routes/restaurants.py`, `tests/test_restaurant_create_update.py`, `README.md`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Implement creating (`POST /restaurants`) and updating (`PUT /restaurants/{id}`) restaurants with JSON persistence, request models, documented 404 error responses, tests, and README endpoint updates.
- Influence: Used the generated implementation, tests and documentation.
- Validation: Ran the full pytest suite locally (46 passing), including tests that new and updated restaurants are saved to the data file, that missing restaurants return 404, that invalid input returns 422, and that the 404 responses appear in the OpenAPI docs. All tests use temporary data files, so the committed `data/restaurants.json` is not modified. Manually tested creating a restaurant, updating one, and requesting a missing id (404) through the FastAPI `/docs` page, and reviewed the implementation by walking through the code and explaining how each layer works.
- PR: [#16](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/16)

### Milestone 2 (Integrated Core System)

#### Entry A6
- Student(s): Anjana Ratnala
- Artifact: `app/schemas/order.py`, `app/repositories/order_repository.py`, `app/services/order_service.py`, `app/core/order_config.py`, `data/orders.json`, `tests/orders/`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: CHECKOUT-03: create and persist a complete order snapshot (customer, restaurant, items, checkout-time prices, total, status) through a new Order Repository.
- Influence: Used the generated implementation and tests.
- Validation: Ran the full pytest suite locally, including tests that the order stores every required field, is saved to JSON, gets a unique ID, survives a restart, keeps its checkout-time price after a menu price change, and that an empty cart creates no order.
- PR: [#111](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/111)

#### Entry A7
- Student(s): Anjana Ratnala
- Artifact: `app/services/order_service.py` (`finalize_checkout`), `tests/orders/test_checkout_finalize.py`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: CHECKOUT-04: save the order first and only then close the cart, leaving the cart unchanged if saving fails.
- Influence: Used the generated implementation and tests.
- Validation: Ran the full pytest suite locally, including a simulated order-save failure that leaves the cart unchanged, a successful checkout that saves the order and closes the cart, rejection of empty or mismatched carts, and a new empty cart after checkout.
- PR: [#112](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/112)

#### Entry A8
- Student(s): Anjana Ratnala
- Artifact: `app/api/routes/orders.py`, `app/services/order_service.py` (`list_orders`, `get_order`), `app/main.py`, `tests/orders/test_order_retrieval.py`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: ORDER-01: let customers retrieve one order and their order history.
- Influence: Used the generated implementation and tests.
- Validation: Ran the full pytest suite locally, including tests for item/price/total/status in the response, newest-first history, 404 for missing and other customers' orders, 401/403 access rules, and orders still being there after a restart.
- PR: [#114](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/114)

#### Entry A9
- Student(s): Anjana Ratnala
- Artifact: `app/schemas/order.py` (`ALLOWED_TRANSITIONS`, `OrderStatusUpdate`), `app/repositories/order_repository.py` (`update_status`, `get_by_restaurant`), `app/services/order_service.py` (`update_status`), `app/api/routes/restaurant_orders.py`, `tests/orders/test_order_lifecycle.py`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: ORDER-02: let a restaurant's owner or an admin move orders through placed, preparing, ready, delivered and completed (or cancelled), rejecting any other transition.
- Influence: Used the generated implementation and tests.
- Validation: Ran the full pytest suite locally, including the full happy path, seven invalid transitions (skipping, going backwards, leaving completed or cancelled), the status being saved to JSON, and 401/403/404/409/422 API responses for wrong roles, other restaurants and bad statuses.
- PR: [#124](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/124)

#### Entry A10
- Student(s): Anjana Ratnala
- Artifact: `app/services/order_service.py` (`cancel_order`), `app/api/routes/orders.py` (`POST .../cancel`), `tests/orders/test_order_cancel.py`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: ORDER-03: let customers cancel their own order while it is still placed.
- Influence: Used the generated implementation and tests.
- Validation: Ran the full pytest suite locally, including cancelling a placed order, rejecting cancellation once preparing, ready, completed or already cancelled, another customer's order, 401/403/404/409 API responses, and the cancelled order staying in the history after a restart.
- PR: [#125](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/125)

#### Entry A11
- Student(s): Anjana Ratnala
- Artifact: `tests/orders/test_order_history_integrity.py`, docstring in `app/services/order_service.py`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: ORDER-04: verify that completed and cancelled orders stay stored and unchanged.
- Influence: Used the generated implementation and tests.
- Validation: Ran the full pytest suite locally, including tests that completed and cancelled orders are retrievable, that items, quantities and checkout-time prices do not change through the lifecycle or after a menu price change or deactivation, and that history survives a restart.
- PR: [#126](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/126)

#### Entry A12
- Student(s): Anjana Ratnala
- Artifact: `app/repositories/json_storage.py`, `app/repositories/menu_item_repository.py`, `tests/test_menu_item_repository_storage.py`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Architectural improvement: move the menu-item repository onto a shared atomic, locked JSON write so a failed or concurrent save can no longer corrupt or lose menu data.
- Influence: Used the generated implementation and tests.
- Validation: Ran the full pytest suite locally, including a regression test that simulates a crash during a menu save and checks the original file is still intact, a concurrency test with parallel availability updates, and the existing menu tests. Read through the code in each file to check it made sense before opening the PR.
- PR: [#128](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/128)

#### Entry A13
- Student(s): Anjana Ratnala
- Artifact: `app/services/place_order_service.py`, `app/api/routes/checkout.py` (`POST /customers/{customer_id}/checkout`), `frontend/cart.html`, `frontend/cart.js`, `frontend/orders.js`, `tests/orders/test_customer_to_order_workflow.py`, `tests/test_cart_frontend.py`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Connect checkout end to end: one endpoint and a Place order button that validate the cart (CHECKOUT-01), re-price it from current menu data (CHECKOUT-02), save the order and only then close the cart (CHECKOUT-03/04), then show the new order.
- Influence: Used the generated implementation and tests.
- Validation: Ran the full pytest suite locally, including the integrated Customer -> Restaurant -> Menu -> Cart -> Checkout -> Order test (register, log in, browse, add to cart, check out, retrieve the order, restart), plus price-change revalidation, an unavailable item blocking checkout with the cart kept, an empty cart, a deactivated customer, another customer's cart, and no token.
- PR: [#143](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/143)

---

## Nandini Anaparti

### Milestone 0 (Foundation Gate)

#### Entry N1
- Student(s): Nandini Anaparti
- Artifact: Dockerfile, compose.yaml
- Label: AI-ASSISTED
- AI tool: Google's "AI mode"
- Purpose: To help set up the Docker configuration
- Influence: Used AI for guidance on configuring Docker, including setting up the Dockerfile and Docker Compose file to run the FastAPI application in a container.
- Validation: Built and ran the application using Docker Compose, and verified that the FastAPI application started successfully and the /health and /docs endpoints were accessible.
- PR: Initial repository setup. See commits [d65984b](https://github.com/Nandini-Anaparti/The-Dispatchers/commit/d65984b) and [481c7c0](https://github.com/Nandini-Anaparti/The-Dispatchers/commit/481c7c0).

### Milestone 1 (First Vertical Slice)

#### Entry N2
- Student(s): Nandini Anaparti
- Artifact: app/services/menu_item_service.py
- Label: AI-REVISED
- AI tool: ChatGPT
- Purpose: To make sure that I rasied the errors correctly and in the right places
- Influence: I wrote the service code myself but used ChatGPT to verify that I raised the errors correctly 
- Validation: Went through the code myself to make sure I understood it, and ran the tests to check that both GET endpoints worked
- PR: [#12](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/12)

#### Entry N3
- Student(s): Nandini Anaparti
- Artifact: app/services/menu_item_service.py, app/api/routes/menu_items.py, tests/test_menu_items.py
- Label: AI-ASSISTED
- AI tool: ChatGPT
- Purpose: To help with writing the route functions for browsing, adding, and updating menu items, as well as tests for the GET, POST, and PUT endpoints.
- Influence: Used AI for guidance on  writing the route functions and figuring out how to test different cases, like when a restaurant or menu item doesn't exist, when an invalid value is entered, and how to make sure changes are saved properly.
- Validation: Wrote and reviewed the code myself to make sure I understood how everything worked. I also ran the tests to check that the GET, POST, and PUT endpoints worked as expected, including handling missing or incorrect IDs, returning the correct errors, and saving changes to the JSON file.
- PR: [#12](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/12) and [#13](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/13)

#### Entry N4
- Student(s): Nandini Anaparti
- Artifact: app/services/menu_item_service.py, app/api/routes/menu_items.py, tests/test_menu_items.py
- Label: AI-ASSISTED
- AI tool: ChatGPT
- Purpose: To help combine the menu item filters, and to help in fixing an issue in the repository's update function.
- Influence: Used AI for guidance on how to combine multiple filters and make sure only the matching menu items were returned. I also used it to help figure out why the update function wasn't working properly and how to fix it.
- Validation: Went through the code myself to make sure I understood how the filtering worked, and ran the tests to check that filtering by name, price, and availability returned the expected results. I also tested the update function to make sure changes were being saved correctly to the JSON file.
- PR: [#14](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/14)

### Milestone 2 (Integrated Core System)

#### Entry N5

- Student(s): Nandini Anaparti
- Artifact: frontend/navbar.js, frontend/styles.css, tests/test_navbar.py
- Label: AI-ASSISTED
- AI tool: ChatGPT
- Purpose: To help with creating the navigation bar and later updating it to show links based on the user's role.
- Influence: Used AI for guidance on setting up the navigation links, checking the user's role through /auth/me.
- Validation: Went through the code myself to make sure I understood how the navigation worked. I also ran the tests and manually checked that the correct links showed up for different users, including after logging in and out.
- PR: [#56](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/56), [#87](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/87)

#### Entry N6

- Student(s): Nandini Anaparti
- Artifact: app/schemas/user.py, app/repositories/user_repository.py, app/services/user_service.py, app/api/routes/customers.py, app/api/routes/restaurant_owners.py, frontend/register.html, frontend/register.js, frontend/owner-register.html, frontend/owner-register.js
- Label: AI-ASSISTED
- AI tool: ChatGPT
- Purpose: To help implement registration for customers and restaurant owners.
- Influence: Used AI for guidance on validating registration information, checking for duplicate emails, and hashing passwords
- Validation: Reviewed the code myself and ran the registration tests to check that users could register successfully, invalid information was rejected, and passwords were saved securely.
- PR: [#63](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/63), [#78](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/78)

#### Entry N7

- Student(s): Nandini Anaparti
- Artifact: app/core/auth.py, app/api/routes/auth.py, app/schemas/auth.py, frontend/login.html, frontend/login.js, tests/test_auth.py, tests/test_login_frontend.py
- Label: AI-ASSISTED
- AI tool: ChatGPT
- Purpose: To help implement backend authentication and connect it to the frontend login and logout functionality.
- Influence: Used AI to help understand JWT authentication, as well as for guidance on checking login credentials, handling invalid or expired tokens, and storing and removing tokens through the frontend.
- Validation: Went through the authentication code to make sure I understood how everything worked. I ran the authentication and login tests, and also tested the endpoints through Swagger. I manually checked that users could log in and out and that incorrect credentials were handled properly.manually.
- PR: [#71](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/71), [#72](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/72)

#### Entry N8

- Student(s): Nandini Anaparti
- Artifact: app/core/permissions.py, app/api/routes/restaurants.py, app/api/routes/menu_items.py, tests/test_role_auth.py
- Label: AI-ASSISTED
- AI tool: ChatGPT
- Purpose: To help with adding role based authorization for customers, restaurant owners, and admins.
- Influence: Used AI for guidance on writing the permission checks and making sure users could only access the functionalities that they were allowed to use. I also used it to help figure out how to test requests made by users who should not have access.
- Validation: Reviewed the code myself and ran the authorization tests and checked that restaurant owners could only manage their own restaurants, customers could not modify restaurants or menus, and admins had the required permissions.
- PR: [#75](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/75)

#### Entry N9

- Student(s): Nandini Anaparti
- Artifact: frontend/menu-management.html, frontend/menu-management.js, app/schemas/menu_item.py, app/repositories/menu_item_repository.py, app/services/menu_item_service.py, app/api/routes/menu_items.py, tests/test_menu_items.py, tests/test_menu_management_frontend.py
- Label: AI-ASSISTED
- AI tool: ChatGPT
- Purpose: To help with implementing the menu management and menu item deactivation.
- Influence: Used ChatGPT for guidance on connecting the frontend forms to the existing menu endpoints. I also used it to help with the deactivation functionality so that menu items could be hidden from customers without being permanently deleted.
- Validation: Went through the code myself and ran the menu tests and full pytest tests. I also tested adding, editing, and deactivating menu items through the frontend and checked that deactivated items were hidden from customers but were still available in the management page for the respective restaurant owner, and the system admins.
- PR: [#79](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/79), [#82](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/82)

---

## Domenica Vizcaino Andrade

### Milestone 2 (Integrated Core System)

#### Entry D1
- Student(s): Domenica Vizcaino Andrade
- Artifact: `docs/M2_BUSINESS_RULES.md`
- Label: AI-REVISED
- AI tool: ChatGPT
- Purpose: Help check the cross-subsystem business-rule plan against the Milestone 2 instructions to make sure everything is covered.
- Influence: After writing the business rules, the LLM helped revise the business rules md file in this project based on the instructions of milestone 2.
- Validation: The initial draft was compared against the supplied M2 instructions and current restaurant/menu code (the only one we have implemented at the moment). Customer/cart/order interfaces still require team agreement and check since they are still being implemented.
- PR: [#51](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/51)

#### Customer Profile
- Student(s): Domenica Vizcaino Andrade
- Artifact: Customer profile API, JSON persistence, My Account page, and profile tests
- Label: AI-ASSISTED
- AI tool: Codex
- Purpose: Implement profile retrieval and updates for signed-in customers.
- Influence: Codex added customer-only endpoints, limited edits to name and delivery address, connected the frontend form, and added regression tests.
- Validation: All 129 pytest tests passed, including tests for persistence, validation, and account isolation.
- PR: [#103](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/103)

#### Customer Address
- Student(s): Domenica Vizcaino Andrade
- Artifact: My Account address form, customer profile API and persistence, and profile tests
- Label: AI-ASSISTED
- AI tool: Codex
- Purpose: Let customers manage delivery addresses through My Account.
- Influence: Codex added structured address validation and preserved the formatted address field used by existing customer records.
- Validation: All 135 pytest tests passed. The address tests cover adding, updating, retrieving, and rejecting missing or blank fields. Checkout integration is pending the checkout implementation.
- PR: [#107](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/107)

#### Entry D2
- Student(s): Domenica Vizcaino Andrade
- Artifact: `app/api/routes/menu_items.py`, `tests/test_role_auth.py`
- Label: AI-ASSISTED
- AI tool: Codex
- Purpose: Make the existing menu management authorization dependency explicit and extend API regression coverage.
- Influence: Codex moved the shared permission check to the route decorators and added coverage for invalid bearer tokens, mismatched restaurant and item IDs, and public item detail access.
- Validation: API tests exercise the routes using temporary JSON data and check that rejected writes leave the menu data intact.
- PR: [#100](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/100)

#### Active Cart Architecture
- Student(s): Domenica Vizcaino Andrade
- Artifact: Cart route, repository, service, and API tests
- Label: AI-ASSISTED
- AI tool: Codex
- Purpose: Enforce authenticated cart ownership and preserve one active cart per customer under concurrent requests.
- Influence: Codex added a reusable ownership dependency and moved active-cart lookup, ID allocation, and saving into one repository operation protected by an in-process lock.
- Validation: Tests exercise authorization and verify that concurrent requests return the same cart ID with one active record in temporary JSON storage.
- PR: [#110](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/110)

#### Cart Integration
- Student(s): Domenica Vizcaino Andrade
- Artifact: Cart routes, service, repository, and API tests
- Label: AI-ASSISTED
- AI tool: Codex
- Purpose: Integrate the cart branches with the ownership and persistence changes already on main.
- Influence: Codex resolved merge conflicts, applied ownership checks across the router, and moved cart mutations into one locked repository operation.
- Validation: API tests cover the combined cart workflow, authorization, invalid menu items, and concurrent item additions.
- PR: [#116](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/116)

#### Customer Order History
- Student(s): Domenica Vizcaino Andrade
- Artifact: Customer Orders page, navigation, and order retrieval tests
- Label: AI-ASSISTED
- AI tool: Codex
- Purpose: Let signed-in customers view their saved orders and item details.
- Influence: Codex connected the page to the team's existing order API and added a regression test for historical prices after menu changes.
- Validation: Tests cover authenticated order retrieval, order ownership, history after menu edits, and frontend asset delivery.
- PR: [#118](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/118)

#### API Documentation
- Student(s): Domenica Vizcaino Andrade
- Artifact: FastAPI route metadata and `tests/test_openapi.py`
- Label: AI-ASSISTED
- AI tool: Codex
- Purpose: Bring the generated OpenAPI contract in line with the Milestone 2 requirements.
- Influence: Codex documented existing error responses, operations, and parameters and added schema regression checks.
- Validation: The OpenAPI tests check descriptions, success response schemas, and expected client errors.
- PR: [#119](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/119).

#### Customer Account Deactivation
- Student(s): Domenica Vizcaino Andrade
- Artifact: Customer deactivation API, My Account confirmation, checkout finalization, and integration tests
- Label: AI-ASSISTED
- AI tool: Codex
- Purpose: Allow customers to deactivate their own account while retaining existing records.
- Influence: Codex added a status-only user update, connected the confirmation flow, and reused the active-customer rule before checkout saves an order.
- Validation: Tests verify persisted deactivation, denied profile and cart access, and rejection of checkout finalization while preserving the cart and existing orders.
- PR: [#117](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/117)

#### Checkout Validation
- Student(s): Domenica Vizcaino Andrade
- Artifact: Checkout validation service, API route, and `tests/cart/test_checkout_validation.py`
- Label: AI-ASSISTED
- AI tool: Codex
- Purpose: Validate the current customer, cart, restaurant, and menu before order placement.
- Influence: Codex added a read-only validation step and integration tests for successful validation and rejected checkout attempts.
- Validation: Tests verify current menu data is used and that validation leaves cart and order files unchanged.
- PR: [#120](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/120).

#### Menu Integration Testing
- Student(s): Domenica Vizcaino Andrade
- Artifact: `tests/test_continuous_integration_and_regression_evidence.py`, `README.md`
- Label: AI-ASSISTED
- AI tool: Codex
- Purpose: Provide cross-subsystem and regression evidence for menu changes between adding an item to the cart and placing an order.
- Influence: Codex helped write the API workflow test, extend the regression cases, and document the test command.
- Validation: Four focused cases and 342 tests in the full suite passed locally. The cases cover current menu prices in the saved order and unchanged cart and order files when an item is unavailable, deactivated, or missing.
- PR: [#144](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/144)

#### Milestone 2 Submission Audit and Cart Page Fix
- Student(s): Domenica Vizcaino Andrade
- Artifact: `README.md`, `docs/PROVENANCE.md`, `frontend/cart.js`, `tests/test_cart_frontend.py`
- Label: AI-ASSISTED
- AI tool: Codex
- Purpose: Verify the live customer workflow against the milestone rubric and update the submission documentation.
- Influence: Codex reconciled the README and provenance with merged PRs, traced a browser checkout failure to the cart loader, and updated the loader and its regression check.
- Validation: With isolated JSON data, headless Chrome verified registration, login, restaurant and menu browsing, adding an item, updating its quantity, and displaying the saved order after checkout.
- PR: Audit changes are local. Related implementation: [#137](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/137) and [#143](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/143).
