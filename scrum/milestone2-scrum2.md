# Sprint Planning – Milestone 2 (Scrum 2)

## Sprint Information

- **Sprint / Milestone:** Milestone 2 – Integrated Core System (feature implementation)
- **Sprint dates:** [2026-11-04 to 2026-11-20]
- **Planning meeting date:** [2026-11-04]
- **Facilitator:** [Ayah Hamdona]
- **Internal deadline:** November 16. **Actual deadline:** November 20.

### Team Members

- [ ] Ayah Hamdona
- [ ] Anjana Ratnala
- [ ] Nandini Anaparti
- [ ] Doménica Vizcaino Andrade

---

## 1. Sprint Goal

> What should the team have working by the end of this sprint?

**Sprint Goal:**

By the end of this sprint, the team will have integrated the independently developed features into one connected core application, so that a customer can move through the workflow **Customer → Restaurant → Menu → Cart → Checkout → Order**. All Milestone 1 restaurant and menu functionality must keep working, and the backend must enforce the business rules and authentication.

The team will finish the required features by the internal deadline of November 16, leaving time before the actual deadline of November 20 for integration, testing, documentation, and the `m2-integrated-system` tag.

---

## 2. User Stories / Sprint Scope

### Authentication and Roles (Nandini)

- [ ] Support authentication and appropriate authorization for customers, restaurant users, and system administrators.
- Epic #31. User stories #38, #39, #40, #77.

### Restaurant Discovery

- [x] List restaurants, search restaurants, filter by cuisine, and retrieve restaurant details. (DONE)

### Menu Management

- [ ] Allow customers to browse menus and authorized restaurant users to add, update, deactivate, and manage menu-item availability.
- Epic #33. User stories #46 (Nandini), #47 (Nandini), #48, #49.

### Customer Accounts

- [ ] Register, sign in, retrieve and update profiles, update delivery addresses, deactivate accounts, and retrieve order history.
- Epic #32. User stories #41 (Nandini), #42, #43, #44, #45.

### Shopping Cart (Ayah)

- [ ] Create an active cart, add items, update quantities, remove items, clear the cart, and calculate totals.

### Checkout and Orders (Ayah)

- [ ] Validate current data, recalculate prices, create a complete order snapshot, save the order, and only then close or clear the cart.

### Order Management (Ayah)

- [ ] Retrieve orders, progress orders through their lifecycle, cancel eligible orders, and preserve completed and cancelled orders.

### Delivery Management (Doménica)

- [ ] Create deliveries, assign drivers, retrieve delivery information, update delivery progress, and complete deliveries.
- Epic #57. User stories #58, #59, #60, #61, #62.
- Milestone update: moved to Milestone 3.

### Reporting (Doménica)

- [ ] Provide read-only reports such as restaurant revenue, most-ordered menu items, and order counts by status.
- Epic #64. User stories #65, #66, #67.
- Milestone update: moved to Milestone 3.

### Optional Features

- [ ] Search and filtering (by menu items and customer locations) – Ayah.
- [ ] Promotions – Anjana.
- [ ] Favourites – Anjana.
- [ ] Notifications – Anjana.
- [ ] Ratings and reviews – Nandini. Epic #34. User stories #52, #53, #54, #55. Milestone update: moved to Milestone 3.
- [ ] Enhanced delivery – Doménica. Epic #68. User story #69. Milestone update: moved to Milestone 3.

### Frontend and Documentation

- [ ] Frontend: all team members. Nandini starts with the navigation bar.
- [ ] Scrum notes formatting: Ayah.
- [ ] Business logic, submission check, and documentation: Doménica.

---

## 3. Task Breakdown and Responsibilities

### Nandini – Authentication, Menu, and Accounts

- [ ] Authentication and roles (epic #31; user stories #38, #39, #40, #77).
- [ ] Menu management user stories #46 and #47.
- [ ] Customer accounts user story #41.
- [ ] Start the frontend with the navigation bar.
- [ ] Optional: ratings and reviews (moved to Milestone 3).

### Ayah – Cart, Checkout, SCRUM, and Orders

- [ ] Shopping cart.
- [ ] Checkout and orders.
- [ ] Order management.
- [ ] Optional: search and filtering by menu items and customer locations.
- [ ] Format the scrum notes.
- [ ] Contribute to the frontend.

### Anjana – Optional Features

- [ ] Optional: promotions, favourites, and notifications.
- [ ] Contribute to the frontend.

### Doménica – Delivery, Reporting, and Submission

- [ ] Delivery management and reporting (moved to Milestone 3).
- [ ] Business logic, submission check, and documentation.
- [ ] Contribute to the frontend.

---

## 4. Dependencies and Integration

| Dependency | Related User Stories | Who is Responsible? | Planned Resolution |
|---|---|---|---|
| Cart, checkout, and order work depend on customer accounts and authentication | Shopping cart; checkout and orders; order management | Ayah + Nandini | Build on the customer and authentication work as it is merged. |
| Frontend pages depend on working backend endpoints | All frontend work | Entire team | Nandini starts with the navigation bar; other pages connect to the REST API as endpoints are available. |
| Final submission depends on all work being merged and reviewed | Entire Milestone 2 | Entire team / Doménica coordinating | Hold a second scrum on November 16 and record it. |

### Integration Plan

Each team member works on a feature branch tied to a GitHub issue with acceptance criteria. Each change is merged through a reviewed Pull Request, and each Pull Request description states the tests that cover it.

The team will connect the customer, restaurant, menu, cart, checkout, and order features through the application's defined interfaces so the full workflow runs end to end, then run the full pytest suite before creating the `m2-integrated-system` tag.

---

## 5. Risks and Potential Blockers

| Risk / Blocker | Impact | Planned Action | Owner |
|---|---|---|---|
| Internal deadline is November 16 and the actual deadline is November 20 | Little time to integrate and fix problems | Meet on Monday, November 16 at 12:30 pm and write another scrum note | Entire team |
| Delivery, reporting, and several optional features compete with the required features | Required cart, checkout, and order work could be delayed | Move delivery, reporting, ratings and reviews, and enhanced delivery to Milestone 3 | Entire team |
| Pull Requests that do not describe their tests | Reviewers cannot confirm coverage | State the tests in every Pull Request | Entire team |

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
- [ ] Documentation has been updated where necessary.
- [ ] The change is integrated into the team's working version.
- [ ] No known critical defects remain.

---

## 7. Sprint Commitment

| Team Member | Initial Responsibilities | Confirmed |
|---|---|---|
| Nandini Anaparti | Authentication and roles, menu management, customer accounts, navigation bar | [x] |
| Anjana Ratnala | Optional features (promotions, favourites, notifications), frontend | [x] |
| Ayah Hamdona | Shopping cart, checkout and orders, order management, scrum notes formatting, frontend | [x] |
| Doménica Vizcaino Andrade | Delivery management, reporting, business logic, submission check and documentation, frontend | [x] |

---

## Meeting Notes

- Reviewed the Milestone 2 features and assigned each one to a team member.
- Internal deadline: November 16. Actual deadline: November 20.
- The team will meet again on Monday, November 16 at 12:30 pm and write another scrum note.
- For Pull Requests, make sure the description says which tests were added.
- Restaurant discovery is done.
- Delivery management, reporting, ratings and reviews, and enhanced delivery were moved to Milestone 3.
- Frontend work is shared by all team members, and Nandini starts with the navigation bar.
- Ayah formats the scrum notes. Doménica handles business logic, the submission check, and documentation.

