from backtest.models import Direction, PositionStatus
from backtest.strategy_position import StrategyVirtualPosition


def test_strategy_virtual_position_represents_strategy_intent():
    position = StrategyVirtualPosition(
        strategy_id="trend",
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        status=PositionStatus.LONG,
        quantity=2,
    )

    assert position.strategy_id == "trend"
    assert position.symbol == "TXF"
    assert position.contract == "TX1"
    assert position.direction == Direction.LONG
    assert position.status == PositionStatus.LONG
    assert position.quantity == 2

import pytest
from pydantic import ValidationError

from backtest.models import Direction, PositionStatus
from backtest.strategy_position import StrategyVirtualPosition


def test_strategy_virtual_position_rejects_zero_quantity():
    with pytest.raises(ValidationError):
        StrategyVirtualPosition(
            strategy_id="trend",
            symbol="TXF",
            contract="TX1",
            direction=Direction.LONG,
            status=PositionStatus.LONG,
            quantity=0,
        )

import pytest
from pydantic import ValidationError

from backtest.models import Direction, PositionStatus
from backtest.strategy_position import StrategyVirtualPosition


def test_strategy_virtual_position_rejects_direction_status_mismatch():
    with pytest.raises(ValidationError):
        StrategyVirtualPosition(
            strategy_id="trend",
            symbol="TXF",
            contract="TX1",
            direction=Direction.LONG,
            status=PositionStatus.SHORT,
            quantity=1,
        )
