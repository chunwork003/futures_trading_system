import pytest

from backtest.fixed_ratio_parameters import FixedRatioParameters


def test_fixed_ratio_parameters_accept_valid_values():
    parameters = FixedRatioParameters(
        initial_equity=1_000_000,
        delta=100_000,
        base_quantity=1,
    )

    assert parameters.initial_equity == 1_000_000
    assert parameters.delta == 100_000
    assert parameters.base_quantity == 1


@pytest.mark.parametrize(
    "field",
    ["initial_equity", "delta", "base_quantity"],
)
def test_fixed_ratio_parameters_reject_non_positive_values(field):
    values = {
        "initial_equity": 1_000_000,
        "delta": 100_000,
        "base_quantity": 1,
    }

    values[field] = 0

    with pytest.raises(ValueError):
        FixedRatioParameters(**values)
