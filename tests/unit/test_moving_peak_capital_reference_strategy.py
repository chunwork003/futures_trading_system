from backtest.capital_reference_strategy import CapitalReferenceStrategy
from backtest.moving_peak_capital_reference import MovingPeakCapitalReference


def test_moving_peak_implements_capital_reference_strategy():
    strategy = MovingPeakCapitalReference(1_000_000)

    assert isinstance(strategy, CapitalReferenceStrategy)
