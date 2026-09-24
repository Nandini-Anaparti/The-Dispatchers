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

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check. Returns `200` and `{"status": "ok"}` |
| GET | `/restaurants` | Returns the list of all restaurants |
| GET | `/restaurants/{restaurant_id}` | Returns one restaurant, or `404` if the id does not exist |
| GET | `/docs` | Interactive OpenAPI (Swagger) documentation |

No API prefix is used. For example, the restaurant list is at http://127.0.0.1:8000/restaurants and the docs are at http://127.0.0.1:8000/docs.

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
