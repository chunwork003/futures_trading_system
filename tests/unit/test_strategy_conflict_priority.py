from backtest.models import Direction, PositionStatus
from backtest.strategy_position import StrategyVirtualPosition
from backtest.strategy_priority_policy import PriorityStrategyConflictPolicy


def test_priority_policy_selects_highest_priority_strategy_direction():
    positions = [
        StrategyVirtualPosition(
            strategy_id="LONG-TERM",
            symbol="TXF",
            contract="TX1",
            direction=Direction.LONG,
            status=PositionStatus.LONG,
            quantity=2,
            priority=5,
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

    policy = PriorityStrategyConflictPolicy()

    assert policy.resolve(positions) == Direction.SHORT
