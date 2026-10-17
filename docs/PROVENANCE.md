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
