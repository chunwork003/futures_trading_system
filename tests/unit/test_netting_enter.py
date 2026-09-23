from backtest.models import Direction
from backtest.netting_calculator import calculate_netting
from backtest.target_position import TargetAccountPosition


def test_calculate_netting_returns_enter_quantity():
    target = TargetAccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=3,
    )

    result = calculate_netting(None, target)

    assert result.action.value == "ENTER"
    assert result.direction == Direction.LONG
    assert result.quantity == 3
