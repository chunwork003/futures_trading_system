from backtest.account_position import AccountPosition
from backtest.models import Direction
from backtest.netting_calculator import calculate_netting


def test_calculate_netting_returns_exit_quantity():
    current = AccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=5,
    )

    result = calculate_netting(current, None)

    assert result.action.value == "EXIT"
    assert result.direction == Direction.LONG
    assert result.quantity == 5
