# Sprint Planning – Milestone 1

## Sprint Information

- **Sprint / Milestone:** Milestone 1 – First Vertical Slice
- **Sprint dates:** [2026-09-29 to 2026-10-16]
- **Planning meeting date:** [2026-09-28]
- **Facilitator:** [Domenica]

### Team Members

- [ ] Ayah Hamdona
- [ ] Anjana Ratnala
- [ ] Nandini Anaparti
- [ ] Doménica Vizcaino Andrade

---

## 1. Sprint Goal

> What should the team have working by the end of this sprint?

**Sprint Goal:**

By the end of this sprint, the team will have a functional and integrated first vertical slice of the food-delivery application focused on restaurant discovery and menu browsing. Customers should be able to view restaurants, select a restaurant to view its details, and access its menu and menu items.

The application will use the required **route → service → repository → JSON/CSV** architecture, Pydantic models, persistent data, automated testing, and a basic frontend connected to the REST API.

The team will also ensure that the implementation is properly documented, tested, reviewed through GitHub Pull Requests, and ready for the Milestone 1 live demonstration and submission.

---

## 2. User Stories / Sprint Scope

### Restaurant Management

- [ ] As a customer, I want to view a list of restaurants so that I can see the available restaurant options.
- [ ] As a customer, I want to view the details of a specific restaurant so that I can learn more about it.
- [ ] As a customer, I want to search or filter restaurants so that I can find restaurants that meet my preferences.
- [ ] As a restaurant manager, I want to create a restaurant so that restaurant information can be added to the system.
- [ ] As a restaurant manager, I want to update restaurant information so that restaurant data remains accurate.
- [ ] Implement Restaurant Pydantic models.
- [ ] Implement restaurant route, service, and repository layers.
- [ ] Persist restaurant data using JSON/CSV.
- [ ] Add unit and API/integration tests for restaurant functionality.

### Menu and Menu Items

- [ ] As a customer, I want to view the menu for a selected restaurant so that I can see what food is available.
- [ ] As a customer, I want to retrieve menu items so that I can view information about individual items.
- [ ] As a restaurant manager, I want to add menu items so that new items can be offered.
- [ ] As a restaurant manager, I want to update menu items so that menu information remains accurate.
- [ ] Implement Menu/Menu Item Pydantic models.
- [ ] Implement menu route, service, and repository layers.
- [ ] Persist menu data using JSON/CSV.
- [ ] Maintain correct relationships between restaurants and their menu items.
- [ ] Add unit and API/integration tests for menu functionality.

### Frontend

- [ ] Display the list of restaurants retrieved from the REST API.
- [ ] Allow users to select a restaurant.
- [ ] Display restaurant details.
- [ ] Display menu/menu-item information for the selected restaurant.
- [ ] Provide an interface for the selected restaurant-management create/update operation.
- [ ] Ensure restaurant and menu data are retrieved from the backend rather than hard-coded in the frontend.

### Testing and CI

- [ ] Test the health endpoint.
- [ ] Test restaurant-list operations.
- [ ] Test repository behavior.
- [ ] Test at least one invalid/failure scenario.
- [ ] Add appropriate tests for implemented frontend/backend functionality.
- [ ] Configure GitHub Actions to install dependencies and automatically run the pytest test suite.
- [ ] Verify that all tests pass in a clean CI environment.

### Documentation and Submission

- [ ] Ensure FastAPI OpenAPI documentation reflects implemented endpoints.
- [ ] Document endpoint descriptions, parameters, request/response models, status codes, and expected errors.
- [ ] Update README.
- [ ] Update `docs/PROVENANCE.md`.
- [ ] Add Scrum meeting notes under `scrum/`.
- [ ] Verify GitHub Project Board and user stories/issues.
- [ ] Verify all implementation was completed through feature branches and reviewed Pull Requests.
- [ ] Prepare contribution percentages.
- [ ] Create the `m1-vertical-slice` tag.
- [ ] Record the full commit SHA.
- [ ] Prepare and submit the Canvas PDF containing the required repository, project board, tag/release, commit, and contribution information.

---

## 3. Task Breakdown and Responsibilities

### Nandini – Backend: Menu and Menu Items

- [ ] Implement menu and menu-item backend functionality.
- [ ] Create appropriate Pydantic models.
- [ ] Implement menu/menu-item routes.
- [ ] Implement menu/menu-item service-layer logic.
- [ ] Implement repository operations for menu/menu-item persistence.
- [ ] Connect menu items to the appropriate restaurants.
- [ ] Support retrieving menu/menu items.
- [ ] Support adding menu items.
- [ ] Support updating menu items.
- [ ] Add unit tests for submitted code.
- [ ] Document relevant API endpoints.

### Anjana – Backend: Restaurants

- [ ] Implement restaurant backend functionality.
- [ ] Create Restaurant Pydantic models.
- [ ] Implement restaurant routes.
- [ ] Implement restaurant service-layer logic.
- [ ] Implement restaurant repository and JSON/CSV persistence.
- [ ] Support retrieving the restaurant list.
- [ ] Support retrieving restaurant details.
- [ ] Support restaurant search/filter functionality.
- [ ] Support creating restaurants.
- [ ] Support updating restaurant information.
- [ ] Add unit tests for submitted code.
- [ ] Document relevant API endpoints.

### Ayah – Frontend

- [ ] Implement the basic frontend for the vertical slice.
- [ ] Connect the frontend to the REST API.
- [ ] Display the restaurant list.
- [ ] Allow users to select and view restaurant details.
- [ ] Display menu/menu-item information.
- [ ] Implement the appropriate interface for the selected restaurant create/update operation.
- [ ] Verify frontend behavior with backend API responses.
- [ ] Ensure restaurant information is not hard-coded.
- [ ] Add appropriate tests where applicable.

### Doménica – Frontend, Testing, Scrum Notes, and Submission

- [ ] Assist with frontend implementation and API integration.
- [ ] Verify the complete customer workflow: **Restaurant List → Search/Filter → Restaurant Details → Menu → Menu Items**.
- [ ] Add/coordinate automated tests for the required functionality.
- [ ] Verify the health endpoint test.
- [ ] Verify restaurant-list tests.
- [ ] Verify repository tests.
- [ ] Verify invalid/failure scenario tests.
- [ ] Help verify integration/API tests.
- [ ] Configure or verify GitHub Actions CI and ensure pytest runs successfully.
- [ ] Maintain Sprint/Scrum meeting notes.
- [ ] Verify README updates.
- [ ] Verify `docs/PROVENANCE.md` updates.
- [ ] Verify required GitHub issues, acceptance criteria, branches, Pull Requests, and reviews are present.
- [ ] Coordinate final integration and testing before submission.
- [ ] Collect team contribution percentages.
- [ ] Verify/create the `m1-vertical-slice` submission tag.
- [ ] Record the final commit SHA.
- [ ] Prepare the Canvas submission PDF.
- [ ] Submit the final Milestone 1 group assignment.

---

## 4. Dependencies and Integration

Identify work that depends on another team member, subsystem, or component.

| Dependency | Related User Stories | Who is Responsible? | Planned Resolution |
|---|---|---|---|
| Frontend requires working restaurant API endpoints | View restaurant list; view restaurant details; search/filter restaurants | Anjana + Ayah/Doménica | Define API contract early and integrate frontend once restaurant endpoints are available. |
| Menu frontend requires working menu/menu-item API endpoints | View restaurant menu; retrieve menu items | Nandini + Ayah/Doménica | Agree on response models and endpoint structure before frontend integration. |
| Menu items must maintain a relationship with restaurants | View menu/menu items for selected restaurant | Nandini + Anjana | Coordinate restaurant IDs and data models so menu data consistently references restaurants. |
| Automated tests depend on stable API and repository behavior | All implemented backend user stories | Entire team / Doménica coordinating | Each developer adds unit tests with their PR; integration tests are completed after components are combined. |
| Final submission depends on all work being merged and reviewed | Entire Milestone 1 | Entire team / Doménica coordinating | Complete PR reviews and integration before creating the final submission tag. |

### Integration Plan

Each team member will implement their assigned work on a separate, meaningfully named feature branch associated with a GitHub user story/issue. Each user story will include acceptance criteria.

When a feature is ready, the developer will open a Pull Request. At least one other team member will review the Pull Request before it is merged. Code submitted through a Pull Request will include appropriate unit tests, and review feedback will be addressed before merging.

Backend restaurant and menu functionality will first be integrated through the agreed API contract. The frontend will then connect to these endpoints to create the complete vertical slice:

**Restaurant List → Search / Filter → Restaurant Details → Menu → Menu Items**

After integration, the team will run the complete pytest suite and verify the GitHub Actions CI workflow. The final integrated version will be tested before creating the immutable `m1-vertical-slice` tag.

---

## 5. Risks and Potential Blockers

Identify anything that could prevent the team from achieving the sprint goal.

| Risk / Blocker | Impact | Planned Action | Owner |
|---|---|---|---|
| Restaurant and menu models/endpoints are inconsistent | Frontend integration or restaurant-menu relationships may fail | Agree on IDs, Pydantic models, endpoint structure, and response formats before integration | Anjana + Nandini |
| Backend functionality is completed late | Frontend and integration testing may be delayed | Prioritize required vertical-slice functionality before optional features | Entire team |
| Merge conflicts between team members | Integration may be delayed | Use separate feature branches, small PRs, and regularly pull/update from the main branch | Entire team |
| Insufficient automated tests or failing CI | Milestone requirements may not be satisfied | Require tests with code PRs and run the complete test suite before final tagging | Doménica + Entire team |
| Missing documentation or submission requirements | Completed functionality may lose marks due to incomplete submission | Use the milestone requirements as a final checklist before submission | Doménica |

---

## 6. Definition of Done

For work to be considered **DONE**, the team agrees that it must satisfy the following:

- [ ] Requirements/acceptance criteria are satisfied.
- [ ] Business logic is implemented in the appropriate service layer.
- [ ] Persistence is handled through the repository layer.
- [ ] Appropriate unit tests are included.
- [ ] Appropriate integration/API tests are included.
- [ ] Tests pass.
- [ ] Code has been reviewed by at least one teammate.
- [ ] Review feedback has been addressed.
- [ ] Documentation has been updated where necessary.
- [ ] The change is integrated into the team's working version.
- [ ] No known critical defects remain.

---

## 7. Sprint Commitment

Before ending the meeting, each team member should confirm their understanding of the sprint plan.

| Team Member | Initial Responsibilities | Confirmed |
|---|---|---|
| Nandini Anaparti | Backend – Menu and Menu Items | [ ] |
| Anjana Ratnala | Backend – Restaurants | [ ] |
| Ayah Hamdona | Frontend | [ ] |
| Doménica Vizcaino Andrade | Frontend, Testing, Scrum Notes, Integration, and Submission | [ ] |

---

## Meeting Notes

- Reviewed the requirements for **Milestone 1 – First Vertical Slice**.
- Agreed to divide the Milestone 1 tasks among team members.
- Nandini will focus on the backend implementation for **Menu and Menu Items**.
- Anjana will focus on the backend implementation for **Restaurants**.
- Ayah will focus primarily on the **Frontend**.
- Doménica will work on the **Frontend, testing, Scrum documentation, final integration, and submission**.
- The team will prioritize the required vertical slice over optional functionality.
- Backend development will follow the required **route → service → repository → JSON/CSV** architecture.
- Frontend restaurant/menu information will be retrieved through the REST API rather than hard-coded.
- Each implemented feature will originate from a GitHub user story/issue with acceptance criteria.
- Implementation will occur on feature branches and be merged through reviewed Pull Requests.
- Appropriate unit tests will accompany submitted code.
- The team will use GitHub Actions to run the pytest suite automatically.
- The team will complete integration and testing before creating the final `m1-vertical-slice` tag.
- Doménica will coordinate the final Milestone 1 submission requirements.
