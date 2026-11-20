"""Regression tests for the menu-item repository storage (architectural improvement).

Before: save_all() opened menu_items.json in "w" mode, which empties the file
immediately. If writing then failed, the file was left empty or half-written,
and every menu, cart and checkout that reads it would break. Concurrent updates
could also overwrite each other because nothing was locked.
"""

import json
import threading

import pytest

from app.repositories import json_storage
from app.repositories.menu_item_repository import MenuItemRepository
from app.schemas.menu_item import MenuItem

ITEMS = [
    {"id": i, "restaurant_id": 1, "name": f"Item{i}", "description": "d",
     "price": 10.0, "is_available": True, "is_active": True}
    for i in range(1, 6)
]


@pytest.fixture
def repo(tmp_path):
    path = tmp_path / "menu_items.json"
    path.write_text(json.dumps(ITEMS), encoding="utf-8")
    return MenuItemRepository(path)


def test_failed_save_leaves_original_file_intact(repo, monkeypatch):
    before = repo.data_path.read_text(encoding="utf-8")

    def crash(*args, **kwargs):
        raise OSError("simulated crash while writing")

    monkeypatch.setattr(json_storage.os, "replace", crash)
    with pytest.raises(OSError):
        repo.deactivate_item(1)

    assert repo.data_path.read_text(encoding="utf-8") == before  # not empty, not half-written
    assert repo.get_by_id(1).is_active is True
    assert not list(repo.data_path.parent.glob("*.tmp"))  # no leftover temp file


def test_successful_save_still_works(repo):
    repo.deactivate_item(2)
    reloaded = MenuItemRepository(repo.data_path)  # like an app restart
    assert reloaded.get_by_id(2).is_active is False
    assert reloaded.get_by_id(2).is_available is False


def test_parallel_updates_do_not_lose_changes(repo):
    def deactivate(item_id):
        MenuItemRepository(repo.data_path).deactivate_item(item_id)

    threads = [threading.Thread(target=deactivate, args=(i,)) for i in range(1, 6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert all(not item.is_active for item in repo.get_all())  # all 5 changes kept


def test_add_item_keeps_existing_items(repo):
    repo.add_item(MenuItem(id=6, restaurant_id=1, name="New", description="d",
                           price=5.0, is_available=True))
    assert [item.id for item in repo.get_all()] == [1, 2, 3, 4, 5, 6]


def test_missing_file_reads_as_empty(tmp_path):
    assert MenuItemRepository(tmp_path / "nope.json").get_all() == []


def test_file_that_is_not_a_list_is_rejected(tmp_path):
    path = tmp_path / "menu_items.json"
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        MenuItemRepository(path).get_all()
