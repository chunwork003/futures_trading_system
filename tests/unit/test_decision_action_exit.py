from backtest.account_position import AccountPosition
from backtest.decision import DecisionAction
from backtest.decision_action import determine_decision_action
from backtest.models import Direction


def test_determine_decision_action_returns_exit_when_target_is_flat():
    current = AccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=2,
    )

    assert determine_decision_action(
        current,
        None,
    ) == DecisionAction.EXIT
