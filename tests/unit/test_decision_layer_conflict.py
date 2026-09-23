from backtest.decision_layer import MultiStrategyDecisionLayer
from backtest.models import Direction, PositionStatus
from backtest.strategy_position import StrategyVirtualPosition
from backtest.strategy_priority_policy import PriorityStrategyConflictPolicy


def test_decision_layer_uses_conflict_policy_for_opposite_directions():
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

    target = MultiStrategyDecisionLayer(
        conflict_policy=PriorityStrategyConflictPolicy(),
    ).decide(positions)

    assert target.direction == Direction.SHORT
    assert target.quantity == 1
