import pytest

from backtest.fixed_amount_sizing import FixedAmountSizing


@pytest.mark.parametrize("amount", [0, -1, -100_000])
def test_fixed_amount_rejects_non_positive_amount(amount):
    with pytest.raises(ValueError):
        FixedAmountSizing(amount=amount)
