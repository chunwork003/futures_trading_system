import pytest
from pydantic import ValidationError

from backtest.position_sizing import PositionSizingInput


def test_position_sizing_input_rejects_non_positive_equity():
    with pytest.raises(ValidationError):
        PositionSizingInput(
            equity=0,
            price=20_000,
            stop_price=19_900,
            multiplier=200,
            risk_budget=0.01,
        )


def test_position_sizing_input_rejects_non_positive_price():
    with pytest.raises(ValidationError):
        PositionSizingInput(
            equity=1_000_000,
            price=0,
            stop_price=19_900,
            multiplier=200,
            risk_budget=0.01,
        )


def test_position_sizing_input_rejects_non_positive_stop_price():
    with pytest.raises(ValidationError):
        PositionSizingInput(
            equity=1_000_000,
            price=20_000,
            stop_price=0,
            multiplier=200,
            risk_budget=0.01,
        )


def test_position_sizing_input_rejects_non_positive_multiplier():
    with pytest.raises(ValidationError):
        PositionSizingInput(
            equity=1_000_000,
            price=20_000,
            stop_price=19_900,
            multiplier=0,
            risk_budget=0.01,
        )


def test_position_sizing_input_rejects_risk_budget_above_one():
    with pytest.raises(ValidationError):
        PositionSizingInput(
            equity=1_000_000,
            price=20_000,
            stop_price=19_900,
            multiplier=200,
            risk_budget=1.01,
        )


def test_position_sizing_input_rejects_negative_risk_budget():
    with pytest.raises(ValidationError):
        PositionSizingInput(
            equity=1_000_000,
            price=20_000,
            stop_price=19_900,
            multiplier=200,
            risk_budget=-0.01,
        )
