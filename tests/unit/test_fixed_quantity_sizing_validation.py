import pytest

from backtest.fixed_quantity_sizing import FixedQuantitySizing


@pytest.mark.parametrize("quantity", [0, -1, -5])
def test_fixed_quantity_rejects_non_positive_quantity(quantity):
    with pytest.raises(ValueError):
        FixedQuantitySizing(quantity=quantity)
