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
- PR: #1 (restored by #9)

#### Entry A2
- Student(s): Anjana Ratnala
- Artifact: `app/services/restaurant_service.py`, `app/api/routes/restaurants.py`, `app/main.py`, `tests/test_restaurant_by_id.py`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Implement the restaurant service and routes (`GET /restaurants`, `GET /restaurants/{id}` with 404 handling) and tests for the by-id endpoint.
- Influence: Used the generated implementation and tests.
- Validation: Ran the full pytest suite locally, including tests that an unknown restaurant id returns 404, and confirmed all tests passed before opening the PR. Reviewed the code and explained it to the TA during the M0 lab demo.
- PR: #2

#### Entry A3
- Student(s): Anjana Ratnala
- Artifact: `README.md`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Write the README (setup, endpoints, tests, project structure).
- Influence: Used the generated documentation.
- Validation: Checked that the documented endpoints, commands and file paths match the actual code and project structure.
- PR: #3

### Milestone 1 (First Vertical Slice)

#### Entry A4
- Student(s): Anjana Ratnala
- Artifact: `app/services/restaurant_service.py`, `app/api/routes/restaurants.py`, `tests/test_restaurant_search.py`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Implement restaurant search and filter on `GET /restaurants` (name, cuisine, is_open, min_rating) and its tests.
- Influence: Used the generated implementation and tests.
- Validation: Ran the full pytest suite locally (35 passing), including tests for each filter, combined filters, no matches, and an invalid `min_rating` returning 422. Manually tested the filters through the FastAPI `/docs` page in the running app, and reviewed the implementation by walking through the code and explaining how each layer works.
- PR: #15

#### Entry A5
- Student(s): Anjana Ratnala
- Artifact: `app/schemas/restaurant.py`, `app/repositories/restaurant_repository.py`, `app/services/restaurant_service.py`, `app/api/routes/restaurants.py`, `tests/test_restaurant_create_update.py`, `README.md`
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Implement creating (`POST /restaurants`) and updating (`PUT /restaurants/{id}`) restaurants with JSON persistence, request models, documented 404 error responses, tests, and README endpoint updates.
- Influence: Used the generated implementation, tests and documentation.
- Validation: Ran the full pytest suite locally (46 passing), including tests that new and updated restaurants are saved to the data file, that missing restaurants return 404, that invalid input returns 422, and that the 404 responses appear in the OpenAPI docs. All tests use temporary data files, so the committed `data/restaurants.json` is not modified. Manually tested creating a restaurant, updating one, and requesting a missing id (404) through the FastAPI `/docs` page, and reviewed the implementation by walking through the code and explaining how each layer works.
- PR: #16

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
- PR: Initial repository setup (no separate PR)

### Milestone 1 (First Vertical Slice)

#### Entry N2
- Student(s): Nandini Anaparti
- Artifact: app/services/menu_item_service.py
- Label: AI-REVISED
- AI tool: ChatGPT
- Purpose: To make sure that I rasied the errors correctly and in the right places
- Influence: I wrote the service code myself but used ChatGPT to verify that I raised the errors correctly 
- Validation: Went through the code myself to make sure I understood it, and ran the tests to check that both GET endpoints worked
- PR: #12

#### Entry N3
- Student(s): Nandini Anaparti
- Artifact: app/services/menu_item_service.py, app/api/routes/menu_items.py, tests/test_menu_items.py
- Label: AI-ASSISTED
- AI tool: ChatGPT
- Purpose: To help with writing the route functions for browsing, adding, and updating menu items, as well as tests for the GET, POST, and PUT endpoints.
- Influence: Used AI for guidance on  writing the route functions and figuring out how to test different cases, like when a restaurant or menu item doesn't exist, when an invalid value is entered, and how to make sure changes are saved properly.
- Validation: Wrote and reviewed the code myself to make sure I understood how everything worked. I also ran the tests to check that the GET, POST, and PUT endpoints worked as expected, including handling missing or incorrect IDs, returning the correct errors, and saving changes to the JSON file.
- PR: #12 and #13

#### Entry N4
- Student(s): Nandini Anaparti
- Artifact: app/services/menu_item_service.py, app/api/routes/menu_items.py, tests/test_menu_items.py
- Label: AI-ASSISTED
- AI tool: ChatGPT
- Purpose: To help combine the menu item filters, and to help in fixing an issue in the repository's update function.
- Influence: Used AI for guidance on how to combine multiple filters and make sure only the matching menu items were returned. I also used it to help figure out why the update function wasn't working properly and how to fix it.
- Validation: Went through the code myself to make sure I understood how the filtering worked, and ran the tests to check that filtering by name, price, and availability returned the expected results. I also tested the update function to make sure changes were being saved correctly to the JSON file.
- PR: #14