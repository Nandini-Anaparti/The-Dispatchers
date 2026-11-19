import os
from pathlib import Path

from app.core.config import PROJECT_ROOT


def get_orders_data_path() -> Path:
    default = PROJECT_ROOT / "data" / "orders.json"
    return Path(os.getenv("ORDERS_DATA_PATH", str(default)))
