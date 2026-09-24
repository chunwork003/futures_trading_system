import pytest

from backtest.fixed_ratio_parameters import FixedRatioParameters
from backtest.fixed_ratio_quantity import calculate_fixed_ratio_quantity


@pytest.fixture
def parameters():
    return FixedRatioParameters(
        initial_equity=1_000_000,
        delta=100_000,
        base_quantity=1,
    )


def test_fixed_ratio_keeps_base_quantity_before_profit_step(parameters):
    assert calculate_fixed_ratio_quantity(
        equity=1_099_999,
        parameters=parameters,
    ) == 1


def test_fixed_ratio_adds_one_quantity_per_profit_step(parameters):
    assert calculate_fixed_ratio_quantity(
        equity=1_100_000,
        parameters=parameters,
    ) == 2


def test_fixed_ratio_adds_multiple_profit_steps(parameters):
    assert calculate_fixed_ratio_quantity(
        equity=1_300_000,
        parameters=parameters,
    ) == 4


def test_fixed_ratio_does_not_reduce_base_quantity_on_loss(parameters):
    assert calculate_fixed_ratio_quantity(
        equity=900_000,
        parameters=parameters,
    ) == 1


@pytest.mark.parametrize("equity", [0, -1])
def test_fixed_ratio_rejects_invalid_equity(parameters, equity):
    with pytest.raises(ValueError):
        calculate_fixed_ratio_quantity(
            equity=equity,
            parameters=parameters,
        )
