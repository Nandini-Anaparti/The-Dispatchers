import json


def test_isolated_data_has_unique_ids(temp_data_file):
    restaurants = json.loads(temp_data_file.read_text(encoding="utf-8"))
    assert len(restaurants) >= 2
    ids = [r["id"] for r in restaurants]
    assert len(ids) == len(set(ids))  # ids must be unique
