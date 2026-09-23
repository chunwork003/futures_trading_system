from backtest.decision import DecisionAction
from backtest.models import Direction
from backtest.netting import NettingResult


def test_netting_result_represents_addition():
    result = NettingResult(
        action=DecisionAction.ADD,
        direction=Direction.LONG,
        quantity=3,
    )

    assert result.action == DecisionAction.ADD
    assert result.direction == Direction.LONG
    assert result.quantity == 3
