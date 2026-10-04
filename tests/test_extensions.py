import pytest

from app import database
from app.calculator import CalculationError, calculate
from app.history import (
    add_record,
    clear_history,
    get_all_records,
    remove_records,
    set_favorite,
    update_metadata,
)


@pytest.mark.parametrize(("expression", "expected"), [
    ("2^3^2", 512), ("sqrt(9)+2^3", 11), ("2^-2", 0.25),
    ("sqrt((3+1)*4)", 4), ("-2^2", -4),
])
def test_scientific(expression, expected):
    assert calculate(expression) == expected


@pytest.mark.parametrize("expression", [
    "0^-1", "2^1001", "sqrt(1,2)", "__import__('os')", "(-2)^0.5", "1e999",
])
def test_invalid_scientific(expression):
    with pytest.raises(CalculationError):
        calculate(expression)


def test_pagination_search_and_clear(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATA_DIRECTORY", tmp_path)
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test.db")
    database.initialize_database()
    for value in range(23):
        add_record(f"{value}+1", value + 1)
    first = get_all_records(page=1)
    last = get_all_records(page=3)
    assert first["total"] == 23
    assert len(first["items"]) == 10
    assert len(last["items"]) == 3
    assert first["items"][0]["expression"] == "22+1"
    record_id = first["items"][0]["id"]
    set_favorite(record_id, True)
    filtered = get_all_records("22+1", True, page=1)
    assert filtered["total"] == 1
    assert filtered["items"][0]["is_favorite"] is True
    assert clear_history() == 23
    assert get_all_records(page=1)["total"] == 0


def test_favorites_first_metadata_and_batch_delete(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATA_DIRECTORY", tmp_path)
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test.db")
    database.initialize_database()
    add_record("1+1", 2)
    add_record("2+2", 4)
    add_record("3+3", 6)
    records = get_all_records()
    favorite_id = records[-1]["id"]
    set_favorite(favorite_id, True)
    update_metadata(favorite_id, "Homework formula", "Useful")

    ordered = get_all_records()
    assert ordered[0]["id"] == favorite_id
    assert ordered[0]["note"] == "Homework formula"
    assert ordered[0]["tag"] == "Useful"
    assert get_all_records("Useful")[0]["id"] == favorite_id

    delete_ids = [ordered[0]["id"], ordered[1]["id"]]
    assert remove_records(delete_ids) == 2
    assert len(get_all_records()) == 1
