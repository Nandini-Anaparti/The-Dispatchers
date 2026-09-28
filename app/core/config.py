"""Application configuration.

The restaurant data location is read from the RESTAURANTS_DATA_PATH
environment variable so tests (and other machines) can point the app at
different data without editing code. If it is not set, the committed
representative data in data/restaurants.json is used.
"""

import os
from pathlib import Path

# Project root = two folders up from this file (app/core/config.py -> project root)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESTAURANTS_PATH = PROJECT_ROOT / "data" / "restaurants.json"


def get_restaurants_data_path() -> Path:
    """Return the path to the restaurant data file.

    This is read every time it is called (not once at import time) so a test
    can set RESTAURANTS_DATA_PATH to a temporary file and the app picks it up.
    """
    return Path(os.getenv("RESTAURANTS_DATA_PATH", str(DEFAULT_RESTAURANTS_PATH)))
