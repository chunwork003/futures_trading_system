from backtest.account_position import AccountPosition
from backtest.decision import DecisionAction
from backtest.decision_action import determine_decision_action
from backtest.models import Direction
from backtest.target_position import TargetAccountPosition


def test_determine_decision_action_returns_add_when_target_quantity_increases():
    current = AccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=2,
    )

    target = TargetAccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=3,
    )

    assert determine_decision_action(current, target) == DecisionAction.ADD
