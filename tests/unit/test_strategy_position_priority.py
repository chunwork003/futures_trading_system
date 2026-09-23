from backtest.models import Direction, PositionStatus
from backtest.strategy_position import StrategyVirtualPosition


def test_strategy_virtual_position_supports_priority():
    position = StrategyVirtualPosition(
        strategy_id="LONG-TERM",
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        status=PositionStatus.LONG,
        quantity=2,
        priority=10,
    )

    assert position.priority == 10
