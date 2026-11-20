# M2 Cross-subsystem business rules

Owner/coordinator: Domenica Vizcaino

## Current status

The Milestone 2 customer-to-order workflow is integrated. The tracker links each business rule to its implementation PRs and the tests that verify it.

## Goal of Cross-Subsystem Business Rules

The following business rules will help the coordinator track the integration of each feature for M2. Then, it will help the coordinator validate the implementation of each change.

## Business rules tracker

**Title:** M2: Enforce and verify cross-subsystem business rules

| Interaction | Business rule | Implementation PR(s) | Implemented by | PR merged by | Validation evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Customer → Cart | A deactivated customer cannot create or modify a cart. | [#116](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/116), [#117](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/117) | Doménica | Nandini (#116), Ayah (#117) | [`test_deactivated_customer_cannot_get_cart`](../tests/cart/test_cart_retrieval.py#L50); [`test_deactivated_and_unknown_customers_rejected`](../tests/cart/test_cart_add_items.py#L49); [`test_deactivated_customer_rejected`](../tests/cart/test_cart_update_quantity.py#L45) | Verified |
| Customer → Cart | Each customer has at most one active cart. | [#101](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/101), [#110](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/110) | Ayah, Doménica | Doménica (#101), Ayah (#110) | [`test_existing_cart_is_retrieved_not_duplicated`](../tests/cart/test_cart_retrieval.py#L17); [`test_concurrent_requests_return_one_active_cart`](../tests/cart/test_cart_retrieval.py#L94) | Verified |
| Restaurant → Cart | A cart can contain items from only one restaurant. | [#104](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/104), [#116](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/116) | Ayah, Doménica | Doménica (#104), Nandini (#116) | [`test_cannot_mix_restaurants_and_cart_stays_unchanged`](../tests/cart/test_cart_add_items.py#L42) | Verified |
| Menu → Cart | Unavailable, deactivated, or nonexistent menu items cannot be added to a new cart. | [#104](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/104), [#116](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/116) | Ayah, Doménica | Doménica (#104), Nandini (#116) | [`test_rejected_items_do_not_create_a_cart`](../tests/cart/test_cart_add_items.py#L65) | Verified |
| Cart | Quantities must be valid. | [#104](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/104), [#105](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/105), [#116](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/116) | Ayah, Doménica | Doménica (#104, #105), Nandini (#116) | [`test_invalid_quantities_rejected`](../tests/cart/test_cart_add_items.py#L29); [`test_invalid_quantity_rejected`](../tests/cart/test_cart_update_quantity.py#L28) | Verified |
| Cart | The backend calculates cart totals. | [#102](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/102), [#129](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/129) | Ayah | Doménica (#102, #129) | [`test_backend_calculates_subtotal_fee_and_total`](../tests/cart/test_cart_totals.py#L15); [`test_client_cannot_override_the_total`](../tests/cart/test_cart_totals.py#L36) | Verified |
| Menu → Checkout | Checkout revalidates current menu-item availability and prices. | [#120](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/120), [#129](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/129), [#143](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/143) | Doménica, Ayah, Anjana | Nandini (#120, #143), Doménica (#129) | [#144](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/144) adds [`test_menu_update_through_api_is_reflected_in_saved_order`](../tests/test_continuous_integration_and_regression_evidence.py#L16); [`test_invalidated_menu_item_blocks_order_and_preserves_storage`](../tests/test_continuous_integration_and_regression_evidence.py#L60) | Verified |
| Customer → Checkout | Checkout requires a valid customer state. | [#117](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/117), [#120](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/120), [#143](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/143) | Doménica, Anjana | Ayah (#117), Nandini (#120, #143) | [`test_deactivated_customer_cannot_check_out`](../tests/orders/test_customer_to_order_workflow.py#L147); [`test_deactivation_blocks_prevalidated_checkout_and_preserves_orders`](../tests/orders/test_checkout_finalize.py#L79) | Verified |
| Cart → Order | An order can be created only from a valid cart. | [#120](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/120), [#143](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/143) | Doménica, Anjana | Nandini (#120, #143) | [`test_customer_to_order_full_workflow`](../tests/orders/test_customer_to_order_workflow.py#L79); [`test_empty_cart_cannot_be_checked_out`](../tests/orders/test_customer_to_order_workflow.py#L140); [`test_checkout_rejects_invalid_stored_quantities`](../tests/cart/test_checkout_validation.py#L105) | Verified |
| Checkout → Persistence | The cart is closed only after the order is successfully persisted. | [#143](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/143) | Anjana | Nandini (#143) | [#112](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/112) adds [`test_successful_checkout_saves_order_and_closes_cart`](../tests/orders/test_checkout_finalize.py#L25); [`test_failed_order_save_leaves_cart_unchanged`](../tests/orders/test_checkout_finalize.py#L37) | Verified |
| Persistence | Customer, restaurant, menu-item, cart, and order relationships survive reloads. | [#143](https://github.com/Nandini-Anaparti/The-Dispatchers/pull/143) | Anjana | Nandini (#143) | [`test_order_and_relationships_survive_restart`](../tests/orders/test_customer_to_order_workflow.py#L100); [`test_cart_is_persisted_and_survives_a_restart`](../tests/cart/test_cart_retrieval.py#L31) | Verified |

## Mandatory execution workflow for each member and evidence

1) Create a GitHub issue and put it in the kanban board (epic/user story) - we can make out tasks as epics (parent issue), and then divide it into subtasks which would be the user stories (sub issues)

2) Create a feature branch through the issue, and implement changes in the branch

3) Move the issue into progress in the Kanban board, and implement it with tests following the required layers: routes, services, repositories, JSON

4) Open a pull request with a description of the feature and its tests. Use Closes #111 (where 111 is issue number) in the PR description so the issue closes when merged into main

5) Teammate review and merge to main, NO self-aproval.

6) Record any AI assistance in PROVENANCE.md
