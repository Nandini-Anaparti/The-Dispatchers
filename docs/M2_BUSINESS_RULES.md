# M2 Cross-subsystem business rules

Owner/coordinator: Domenica Vizcaino

## Current status

Scrum sprint 1 (November 6, 2026): This is the business rules plan made before implementation of the M2 components. At this stage we only have the restaurant and menu modules (at this point we are missing: customer, cart, checkout, or order modules to complete M2). Features are being implemented in this first sprint, while architectural improvement will be implemented and updated in the second scrum sprint cycle of M2. This plan (issues and integration-tests) is based on the M2 section 4 instructions.

## Goal of Cross-Subsystem Business Rules

The following business rules will help the coordinator track the integration of each feature for M2. Then, it will help the coordinator validate the implementation of each change.

## Business rules tracker

**Title:** M2: Enforce and verify cross-subsystem business rules

| Interaction | Business rule | Implementation PR(s) | Implemented by | PR merged by | Validation evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Customer → Cart | A deactivated customer cannot create or modify a cart. | — | — | — | Pending: deactivate a customer and verify cart creation and modifications are rejected without changing saved cart data. | Not verified |
| Customer → Cart | Each customer has at most one active cart. | — | — | — | Pending: repeatedly create/retrieve a customer's active cart and verify only one active cart exists. | Not verified |
| Restaurant → Cart | A cart can contain items from only one restaurant. | — | — | — | Pending: add an item from a second restaurant; verify rejection and unchanged cart contents. | Not verified |
| Menu → Cart | Unavailable, deactivated, or nonexistent menu items cannot be added to a new cart. | — | — | — | Pending: test each invalid item state and verify no item is added. | Not verified |
| Cart | Quantities must be valid. | — | — | — | Pending: test invalid quantities for adding and updating items; verify rejection and unchanged cart contents. | Not verified |
| Cart | The backend calculates cart totals. | — | — | — | Pending: compare backend subtotal and total with independently calculated expected values; verify client values cannot override them. | Not verified |
| Menu → Checkout | Checkout revalidates current menu-item availability and prices. | — | — | — | Pending: change availability after adding an item and verify checkout rejects it; change the price and verify checkout uses the current price. | Not verified |
| Customer → Checkout | Checkout requires a valid customer state. | — | — | — | Pending: deactivate a customer after cart creation and verify checkout fails without creating an order or clearing the cart. | Not verified |
| Cart → Order | An order can be created only from a valid cart. | — | — | — | Pending: verify a valid cart creates an order and invalid carts are rejected without creating orders. | Not verified |
| Checkout → Persistence | The cart is not cleared until the order is successfully persisted. | — | — | — | Pending: simulate an order-save failure and verify the cart is retained; verify successful checkout saves the order before clearing/closing the cart. | Not verified |
| Persistence | Relationships among customers, restaurants, menu items, carts, and orders remain valid after restarts. | — | — | — | Pending: save related data, restart/recreate application instances, and verify persisted relationships still resolve. | Not verified |

## Mandatory execution workflow for each member and evidence

1) Create a GitHub issue and put it in the kanban board (epic/user story) - we can make out tasks as epics (parent issue), and then divide it into subtasks which would be the user stories (sub issues)

2) Create a feature branch through the issue, and implement changes in the branch

3) Move the issue into progress in the Kanban board, and implement it with tests following the required layers: routes, services, repositories, JSON

4) Open a pull request with a description of the feature and its tests. Use Closes #111 (where 111 is issue number) in the PR description so the issue closes when merged into main

5) Teammate review and merge to main, NO self-aproval.

6) Record any AI assistance in PROVENANCE.md
