import pytest

from backtest.position_sizing import PositionSizingStrategy


def test_position_sizing_strategy_is_abstract():
    with pytest.raises(TypeError):
        PositionSizingStrategy()
