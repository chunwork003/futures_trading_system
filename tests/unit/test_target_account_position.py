from backtest.models import Direction
from backtest.strategy_position import StrategyVirtualPosition
from backtest.target_position import TargetAccountPosition


def test_target_account_position_represents_final_account_target():
    position = TargetAccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=2,
    )

    assert position.symbol == "TXF"
    assert position.contract == "TX1"
    assert position.direction == Direction.LONG
    assert position.quantity == 2
