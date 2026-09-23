from backtest.decision import DecisionAction
from backtest.decision_action import determine_decision_action
from backtest.models import Direction
from backtest.target_position import TargetAccountPosition


def test_determine_decision_action_returns_enter_when_current_is_flat():
    target = TargetAccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=2,
    )

    assert determine_decision_action(
        None,
        target,
    ) == DecisionAction.ENTER
