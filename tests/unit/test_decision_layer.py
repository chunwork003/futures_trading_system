from backtest.decision_layer import MultiStrategyDecisionLayer
from backtest.models import Direction, PositionStatus
from backtest.strategy_position import StrategyVirtualPosition


def test_decision_layer_combines_same_direction_positions():
    positions = [
        StrategyVirtualPosition(
            strategy_id="trend",
            symbol="TXF",
            contract="TX1",
            direction=Direction.LONG,
            status=PositionStatus.LONG,
            quantity=2,
        ),
        StrategyVirtualPosition(
            strategy_id="short_term",
            symbol="TXF",
            contract="TX1",
            direction=Direction.LONG,
            status=PositionStatus.LONG,
            quantity=1,
        ),
    ]

    target = MultiStrategyDecisionLayer().decide(positions)

    assert target.direction == Direction.LONG
    assert target.quantity == 3
