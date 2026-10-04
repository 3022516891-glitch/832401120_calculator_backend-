import pytest

from app import database
from app.calculator import CalculationError, calculate
from app.history import add_record, clear_history, get_all_records, set_favorite


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
