import pytest

from backtest.capital_reference_strategy import CapitalReferenceStrategy
from backtest.moving_average_capital_reference import MovingAverageCapitalReference


def test_moving_average_uses_available_equity_history():
    strategy = MovingAverageCapitalReference(window=3)

    assert strategy.update(1_000_000) == 1_000_000
    assert strategy.update(1_100_000) == 1_050_000


def test_moving_average_uses_configured_window():
    strategy = MovingAverageCapitalReference(window=3)

    assert strategy.update(1_000_000) == 1_000_000
    assert strategy.update(1_100_000) == 1_050_000
    assert strategy.update(1_200_000) == 1_100_000
    assert strategy.update(1_300_000) == 1_200_000


def test_moving_average_implements_capital_reference_strategy():
    strategy = MovingAverageCapitalReference(window=5)

    assert isinstance(strategy, CapitalReferenceStrategy)


@pytest.mark.parametrize("window", [0, -1])
def test_moving_average_rejects_invalid_window(window):
    with pytest.raises(ValueError):
        MovingAverageCapitalReference(window=window)


@pytest.mark.parametrize("equity", [0, -1])
def test_moving_average_rejects_non_positive_equity(equity):
    strategy = MovingAverageCapitalReference(window=3)

    with pytest.raises(ValueError):
        strategy.update(equity)
