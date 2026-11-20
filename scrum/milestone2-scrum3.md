# Sprint Planning – Milestone 2 (Scrum 3)

## Sprint Information

- **Sprint / Milestone:** Milestone 2 – Integrated Core System (re-plan of the remaining work)
- **Sprint dates:** [2026-11-16 to 2026-11-20]
- **Planning meeting date:** [2026-11-16, 12:30 pm]
- **Facilitator:** [Ayah Hamdona]

### Team Members

- [ ] Ayah Hamdona
- [ ] Anjana Ratnala
- [ ] Nandini Anaparti
- [ ] Doménica Vizcaino Andrade

---

## 1. Sprint Goal

> What should the team have working by the end of this sprint?

**Sprint Goal:**

By Friday at 1:30 pm, the team will have finished the remaining Milestone 2 issues so the connected workflow **Customer → Restaurant → Menu → Cart → Checkout → Order** runs end to end. The remaining work is ordered by its dependencies, because the first plan did not account for them.

The team will also complete the architectural improvements, regression testing, provenance, README updates, Kanban board updates, and the submission documents, and will then create the tag.

---

## 2. User Stories / Sprint Scope

These are the issues remaining to be completed.

### Shared Frontend Navigation Bar (Nandini)

- [ ] As a user, I want a consistent navigation system so that I can move between sections of the application. Epic #35. User story #37.

### Authentication and Roles (Doménica)

- [ ] Architectural improvement.

### Menu Management (Doménica)

- [ ] Allow customers to browse menus and authorized restaurant users to add, update, deactivate, and manage menu-item availability. Epic #33. User stories #48 and #49.
- [ ] #49 needs order, cart, and checkout to be ready.

### Customer Accounts (Doménica)

- [ ] Register, sign in, retrieve and update profiles, update delivery addresses, deactivate accounts, and retrieve order history. Epic #32. User stories #42, #43, #44, #45.

### Shopping Cart (Ayah) – Epic 1

Authenticated customers create, retrieve, and manage an active cart while the backend enforces restaurant, menu-item, and quantity restrictions.

- [ ] CART-01: As a customer, I want to create or retrieve my active shopping cart so that I can manage the items I intend to order.
- [ ] CART-02: As a customer, I want to add available menu items to my cart so that I can prepare my food order.
- [ ] CART-03: As a customer, I want to change the quantity of items in my cart so that I can adjust my order before checkout.
- [ ] CART-04: As a customer, I want to remove individual items from my cart so that I can change my order without clearing everything.
- [ ] CART-05: As a customer, I want to clear my shopping cart so that I can start a new order.
- [ ] CART-06: As a customer, I want to view my cart contents and its calculated total so that I know what I am ordering and how much it costs.

### Checkout and Orders – Epic 2 (Ayah for S1, Doménica for S2, Anjana for S3 and S4)

The checkout validates current customer, restaurant, menu, and cart information, recalculates prices, creates and persists an order, and clears the cart only after the order is saved.

- [ ] CHECKOUT-01: As a customer, I want my cart and account information validated before checkout so that I can only place valid orders.
- [ ] CHECKOUT-02: As a customer, I want the system to recalculate prices during checkout so that my order reflects current menu prices.
- [ ] CHECKOUT-03: As a customer, I want my order to contain a complete record of my purchase so that I can retrieve the transaction details later.
- [ ] CHECKOUT-04: As a customer, I want my cart to be cleared only after my order has been saved so that I do not lose my items if checkout fails.

### Order Management (Anjana) – Epic 3

Retrieve and manage orders while preserving order records, supporting valid status transitions, and supporting cancellation.

- [ ] ORDER-01: As a customer, I want to retrieve my orders so that I can review my purchases and track their status.
- [ ] ORDER-02: As an authorized restaurant staff member, I want to update order statuses so that orders can progress through their lifecycle. Suggested lifecycle: placed → preparing → ready → delivered → completed, with cancellation allowed only from designated eligible states. The team will agree on the precise statuses.
- [ ] ORDER-03: As a customer, I want to cancel an eligible order so that I can stop an order I no longer want.
- [ ] ORDER-04: As a customer, I want completed and cancelled orders to remain in my order history so that I can review previous transactions.

---

## 3. Task Breakdown and Responsibilities

### Ayah

- [ ] Cart frontend.
- [ ] Checkout 2.
- [ ] Write the two scrum notes.
- [ ] Show regression testing (verify).
- [ ] Architectural improvement.
- [ ] Provenance.
- [ ] README updates.
- [ ] In `frontend/navbar.js`, change the line 11 value from false to true.
- [ ] Check that her part is marked Done on the Kanban board.

### Anjana

- [ ] Order 2, Order 3, and Order 4.
- [ ] Show regression testing (verify).
- [ ] Architectural improvement.
- [ ] Provenance.
- [ ] README updates.
- [ ] Check that her part is marked Done on the Kanban board.

### Doménica

- [ ] Menu management #49 – waiting for Checkout 2 to be ready.
- [ ] Show regression testing (verify).
- [ ] Check that her part is marked Done on the Kanban board.

### Nandini

- [ ] Architectural improvement.
- [ ] Show regression testing (verify).
- [ ] Provenance.
- [ ] README updates.
- [ ] Check that her part is marked Done on the Kanban board.

### Whole team

- [ ] The tag will be created on Friday at 1:30 pm.
- [ ] Submission documents.

---

## 4. Dependencies and Integration

| Dependency | Related User Stories | Who is Responsible? | Planned Resolution |
|---|---|---|---|
| Cart stories depend on customer accounts, authentication, and the menu repository | CART-01 to CART-06 | Ayah | Build on the accounts and authentication already merged. CART-03, CART-04, and CART-05 also need CART-06 totals. |
| Checkout validation depends on the cart | CHECKOUT-01 | Ayah | Finish CART-01, CART-02, and CART-06 first. |
| Price recalculation depends on validation and the cart totals | CHECKOUT-02 | Ayah | Build after CHECKOUT-01 and CART-06. |
| The order snapshot depends on validation and pricing | CHECKOUT-03 | Anjana | Build after CHECKOUT-01 and CHECKOUT-02. |
| Finalizing checkout depends on the order snapshot and clearing the cart | CHECKOUT-04 | Anjana | Build after CHECKOUT-03 and CART-05. |
| Order retrieval depends on the order snapshot | ORDER-01 | Anjana | Build after CHECKOUT-03. |
| Order lifecycle and cancellation depend on order retrieval and role authorization | ORDER-02, ORDER-03, ORDER-04 | Anjana | Build in order after ORDER-01. |
| Menu management #49 needs order, cart, and checkout ready | #49 | Doménica + Ayah | Doménica waits for Checkout 2 to be ready. |

### Integration Plan

Work is merged in dependency order through reviewed Pull Requests, and each description states its tests. After the cart, checkout, and order features are merged, the team verifies the full workflow **Customer → Restaurant → Menu → Cart → Checkout → Order**, shows regression testing, and runs the full pytest suite before the tag is created on Friday at 1:30 pm.

---

## 5. Risks and Potential Blockers

| Risk / Blocker | Impact | Planned Action | Owner |
|---|---|---|---|
| The work was not divided well and did not account for dependencies and the time frame | Features are blocked waiting on earlier ones | Re-plan the remaining issues in dependency order (this meeting) | Entire team |
| Menu management #49 cannot be done until order, cart, and checkout are ready | #49 is delayed | Doménica waits for Checkout 2 to be ready | Doménica + Ayah |
| The tag is created on Friday at 1:30 pm | Little time left for fixes | Finish each person's parts, tests, and documentation before Friday | Entire team |

---

## 6. Definition of Done

- [ ] Requirements/acceptance criteria are satisfied.
- [ ] Business logic is implemented in the appropriate service layer.
- [ ] Persistence is handled through the repository layer.
- [ ] Appropriate unit tests are included.
- [ ] Appropriate integration/API tests are included.
- [ ] Tests pass.
- [ ] The Pull Request description states the tests.
- [ ] Code has been reviewed by at least one teammate.
- [ ] Review feedback has been addressed.
- [ ] Regression testing is shown (verified).
- [ ] Documentation (README and provenance) has been updated.
- [ ] The card is marked Done on the Kanban board.
- [ ] No known critical defects remain.

---

## 7. Sprint Commitment

| Team Member | Initial Responsibilities | Confirmed |
|---|---|---|
| Nandini Anaparti | Shared navigation bar, architectural improvement, regression testing, provenance, README | [x] |
| Anjana Ratnala | Order 2, 3, and 4, architectural improvement, regression testing, provenance, README | [x] |
| Ayah Hamdona | Cart frontend, Checkout 2, scrum notes, architectural improvement, regression testing, provenance, README, navigation bar change | [x] |
| Doménica Vizcaino Andrade | Menu management #48 and #49, customer accounts, authentication architectural improvement, regression testing | [x] |

---

## Meeting Notes

- The work was not divided well, and the team did not think about dependencies and the time frame. The remaining issues were listed and re-planned in dependency order.
- Menu management #49 is waiting for Checkout 2 to be ready.
- Each member shows regression testing (verify), completes an architectural improvement, and checks that their part is marked Done on the Kanban board.
- The tag will be created on Friday at 1:30 pm, followed by the submission documents.
