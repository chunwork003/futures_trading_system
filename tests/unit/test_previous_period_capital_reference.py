import pytest

from backtest.capital_reference_strategy import CapitalReferenceStrategy
from backtest.previous_period_capital_reference import PreviousPeriodCapitalReference


def test_previous_period_uses_previous_days_equity():
    strategy = PreviousPeriodCapitalReference(days=2)

    assert strategy.update(1_000_000) == 1_000_000
    assert strategy.update(1_100_000) == 1_100_000
    assert strategy.update(1_200_000) == 1_000_000


def test_previous_period_uses_configured_days():
    strategy = PreviousPeriodCapitalReference(days=3)

    assert strategy.update(1_000_000) == 1_000_000
    assert strategy.update(1_100_000) == 1_100_000
    assert strategy.update(1_200_000) == 1_200_000
    assert strategy.update(1_300_000) == 1_000_000


def test_previous_period_implements_capital_reference_strategy():
    strategy = PreviousPeriodCapitalReference(days=5)

    assert isinstance(strategy, CapitalReferenceStrategy)


@pytest.mark.parametrize("days", [0, -1])
def test_previous_period_rejects_invalid_days(days):
    with pytest.raises(ValueError):
        PreviousPeriodCapitalReference(days=days)


@pytest.mark.parametrize("equity", [0, -1])
def test_previous_period_rejects_non_positive_equity(equity):
    strategy = PreviousPeriodCapitalReference(days=2)

    with pytest.raises(ValueError):
        strategy.update(equity)
