import pytest
from app.calculator import CalculationError, calculate
from app import database
from app.history import add_record, get_all_records


@pytest.mark.parametrize("expression,mode,expected", [
    ("sin(30)", "DEG", 0.5), ("cos(60)", "DEG", 0.5),
    ("tan(45)", "DEG", 1), ("sin(pi/2)", "RAD", 1),
    ("log(100)", "DEG", 2), ("ln(e)", "DEG", 1),
    ("1/(4)", "DEG", 0.25), ("sqrt(9)+ln(e)", "DEG", 4),
])
def test_scientific_functions(expression, mode, expected):
    assert calculate(expression, mode) == pytest.approx(expected)


@pytest.mark.parametrize("expression", [
    "log(0)", "ln(-1)", "tan(90)", "1/(0)", "sin(1,2)",
    "math.sin(1)", "open('file')", "sin(1e100*1e100*1e100*1e100)",
])
def test_invalid_functions(expression):
    with pytest.raises(CalculationError):
        calculate(expression)


def test_history_keeps_angle_mode(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATA_DIRECTORY", tmp_path)
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test.db")
    database.initialize_database()
    add_record("sin(pi/2)", 1, "RAD")
    assert get_all_records()[0]["angle_mode"] == "RAD"
