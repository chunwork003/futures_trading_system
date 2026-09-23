import pytest

from backtest.models import Direction, PositionStatus
from backtest.strategy_conflict_policy import StrategyConflictPolicy
from backtest.strategy_position import StrategyVirtualPosition


def test_strategy_conflict_policy_requires_resolution_rule():
    positions = [
        StrategyVirtualPosition(
            strategy_id="LONG-TERM",
            symbol="TXF",
            contract="TX1",
            direction=Direction.LONG,
            status=PositionStatus.LONG,
            quantity=2,
        ),
        StrategyVirtualPosition(
            strategy_id="SHORT-TERM",
            symbol="TXF",
            contract="TX1",
            direction=Direction.SHORT,
            status=PositionStatus.SHORT,
            quantity=1,
        ),
    ]

    with pytest.raises(NotImplementedError):
        StrategyConflictPolicy().resolve(positions)
