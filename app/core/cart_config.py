import os
from pathlib import Path


def get_carts_data_path() -> Path:
    default = Path(__file__).resolve().parent.parent.parent / "data" / "carts.json"
    return Path(os.environ.get("CARTS_DATA_PATH", default))

