import pytest

from backtest.account_position import AccountPosition
from backtest.models import Direction
from backtest.netting_calculator import calculate_netting
from backtest.target_position import TargetAccountPosition


def test_calculate_netting_rejects_direction_change():
    current = AccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=3,
    )

    target = TargetAccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.SHORT,
        quantity=2,
    )

    with pytest.raises(
        NotImplementedError,
        match="position identity changes are not implemented",
    ):
        calculate_netting(current, target)
