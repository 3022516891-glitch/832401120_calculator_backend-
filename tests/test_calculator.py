import pytest
from app.calculator import CalculationError, calculate


@pytest.mark.parametrize(("expression", "expected"), [
    ("1 + 2 * 3", 7), ("(1 + 2) * 3", 9), ("3.5 * 2", 7),
    ("5 + -8", -3), ("12 ÷ 4", 3),
    ("5^2", 25), ("2**3", 8), ("sqrt(81)", 9),
])
def test_valid_expression(expression: str, expected: int | float) -> None:
    assert calculate(expression) == expected


@pytest.mark.parametrize("expression", ["", "1/0", "abc", "sqrt(-1)", "True"])
def test_invalid_expression(expression: str) -> None:
    with pytest.raises(CalculationError):
        calculate(expression)
