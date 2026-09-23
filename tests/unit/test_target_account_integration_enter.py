from backtest.decision import DecisionAction
from backtest.decision_action import determine_decision_action
from backtest.models import Direction
from backtest.target_position import TargetAccountPosition


def test_target_account_position_integration_returns_enter_when_account_is_flat():
    current = None

    target = TargetAccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=2,
    )

    assert determine_decision_action(
        current,
        target,
    ) == DecisionAction.ENTER
