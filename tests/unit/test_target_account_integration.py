from backtest.account_position import AccountPosition
from backtest.decision import DecisionAction
from backtest.decision_action import determine_decision_action
from backtest.decision_layer import MultiStrategyDecisionLayer
from backtest.models import Direction, PositionStatus
from backtest.strategy_position import StrategyVirtualPosition


def test_target_account_position_integrates_with_account_decision():
    current = AccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=1,
    )

    strategy_positions = [
        StrategyVirtualPosition(
            strategy_id="LONG-TERM",
            symbol="TXF",
            contract="TX1",
            direction=Direction.LONG,
            status=PositionStatus.LONG,
            quantity=2,
        ),
    ]

    target = MultiStrategyDecisionLayer().decide(strategy_positions)

    assert target.symbol == "TXF"
    assert target.contract == "TX1"
    assert target.direction == Direction.LONG
    assert target.quantity == 2

    assert determine_decision_action(
        current,
        target,
    ) == DecisionAction.ADD
