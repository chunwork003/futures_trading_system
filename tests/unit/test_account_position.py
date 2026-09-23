from backtest.account_position import AccountPosition
from backtest.models import Direction


def test_account_position_represents_current_physical_position():
    position = AccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=2,
    )

    assert position.symbol == "TXF"
    assert position.contract == "TX1"
    assert position.direction == Direction.LONG
    assert position.quantity == 2
