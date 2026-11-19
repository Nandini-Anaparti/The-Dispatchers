"""Shared helpers for reading and safely writing JSON list files.

Atomic write: the data goes to a temporary file first and is then swapped in
with one rename. If anything fails before the rename, the original file is
untouched, so a crash can never leave a half-written or empty data file.
"""

import json
import os
from pathlib import Path


def read_json_list(path: Path) -> list:
    path = Path(path)
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path.name} must contain a JSON list")
    return data


def write_json_list_atomic(path: Path, records: list) -> None:
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_text(json.dumps(records, indent=2), encoding="utf-8")
        os.replace(tmp, path)  # one atomic step
    finally:
        if tmp.exists():  # clean up if the write failed part way
            tmp.unlink()
