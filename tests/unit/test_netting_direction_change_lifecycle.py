from backtest.account_position import AccountPosition
from backtest.models import Direction
from backtest.netting import NettingResult
from backtest.netting_calculator import calculate_netting
from backtest.target_position import TargetAccountPosition


def test_direction_change_netting_requires_exit_first():
    current = AccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=1,
    )

    target = TargetAccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.SHORT,
        quantity=1,
    )

    result = calculate_netting(
        current=current,
        target=target,
    )

    assert isinstance(result, NettingResult)
    assert result.action.value == "EXIT"
    assert result.direction == Direction.LONG
    assert result.quantity == 1
