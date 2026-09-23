from backtest.account_position import AccountPosition
from backtest.models import Direction
from backtest.netting_calculator import calculate_netting
from backtest.target_position import TargetAccountPosition


def test_calculate_netting_returns_reduce_quantity():
    current = AccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=5,
    )

    target = TargetAccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=2,
    )

    result = calculate_netting(current, target)

    assert result.action.value == "REDUCE"
    assert result.direction == Direction.LONG
    assert result.quantity == 3
