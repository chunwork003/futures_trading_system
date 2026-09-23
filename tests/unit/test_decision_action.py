from backtest.decision import DecisionAction


def test_decision_action_contains_account_decision_actions():
    assert DecisionAction.HOLD.value == "HOLD"
    assert DecisionAction.ADD.value == "ADD"
    assert DecisionAction.REDUCE.value == "REDUCE"
    assert DecisionAction.EXIT.value == "EXIT"
    assert DecisionAction.ENTER.value == "ENTER"
