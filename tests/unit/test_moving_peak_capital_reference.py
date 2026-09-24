import pytest

from backtest.moving_peak_capital_reference import MovingPeakCapitalReference


def test_moving_peak_keeps_initial_equity():
    reference = MovingPeakCapitalReference(1_000_000)

    assert reference.update(900_000) == 1_000_000


def test_moving_peak_moves_up_when_equity_increases():
    reference = MovingPeakCapitalReference(1_000_000)

    assert reference.update(1_100_000) == 1_100_000


def test_moving_peak_keeps_highest_equity():
    reference = MovingPeakCapitalReference(1_000_000)

    assert reference.update(1_100_000) == 1_100_000
    assert reference.update(1_050_000) == 1_100_000
    assert reference.update(1_200_000) == 1_200_000


@pytest.mark.parametrize("equity", [0, -1])
def test_moving_peak_rejects_non_positive_equity(equity):
    reference = MovingPeakCapitalReference(1_000_000)

    with pytest.raises(ValueError):
        reference.update(equity)
