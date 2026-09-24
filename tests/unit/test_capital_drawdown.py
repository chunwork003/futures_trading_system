import pytest

from backtest.capital_drawdown import calculate_capital_drawdown


def test_capital_drawdown_is_zero_when_equity_is_above_reference():
    assert calculate_capital_drawdown(
        equity=1_100_000,
        reference_equity=1_000_000,
    ) == 0.0


def test_capital_drawdown_is_zero_when_equity_equals_reference():
    assert calculate_capital_drawdown(
        equity=1_000_000,
        reference_equity=1_000_000,
    ) == 0.0


def test_capital_drawdown_calculates_percentage():
    assert calculate_capital_drawdown(
        equity=900_000,
        reference_equity=1_000_000,
    ) == pytest.approx(0.10)


def test_capital_drawdown_calculates_deeper_loss():
    assert calculate_capital_drawdown(
        equity=750_000,
        reference_equity=1_000_000,
    ) == pytest.approx(0.25)


@pytest.mark.parametrize("equity", [0, -1])
def test_capital_drawdown_rejects_invalid_equity(equity):
    with pytest.raises(ValueError):
        calculate_capital_drawdown(equity, 1_000_000)


@pytest.mark.parametrize("reference_equity", [0, -1])
def test_capital_drawdown_rejects_invalid_reference(reference_equity):
    with pytest.raises(ValueError):
        calculate_capital_drawdown(900_000, reference_equity)
