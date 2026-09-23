import pytest

from backtest.models import Direction, PositionStatus
from backtest.strategy_position import StrategyVirtualPosition
from backtest.strategy_priority_policy import PriorityStrategyConflictPolicy


def test_priority_policy_rejects_equal_priority_conflict():
    positions = [
        StrategyVirtualPosition(
            strategy_id="LONG-TERM",
            symbol="TXF",
            contract="TX1",
            direction=Direction.LONG,
            status=PositionStatus.LONG,
            quantity=2,
            priority=10,
        ),
        StrategyVirtualPosition(
            strategy_id="SHORT-TERM",
            symbol="TXF",
            contract="TX1",
            direction=Direction.SHORT,
            status=PositionStatus.SHORT,
            quantity=1,
            priority=10,
        ),
    ]

    with pytest.raises(
        ValueError,
        match="equal priority",
    ):
        PriorityStrategyConflictPolicy().resolve(positions)
