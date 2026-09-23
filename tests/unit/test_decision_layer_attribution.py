from backtest.decision_layer import MultiStrategyDecisionLayer
from backtest.models import Direction, PositionStatus
from backtest.strategy_position import StrategyVirtualPosition


def test_decision_layer_preserves_strategy_attributions():
    positions = [
        StrategyVirtualPosition(
            strategy_id="LONG-TERM",
            symbol="TXF",
            contract="TX1",
            direction=Direction.LONG,
            status=PositionStatus.LONG,
            quantity=2,
        ),
        StrategyVirtualPosition(
            strategy_id="SHORT-TERM",
            symbol="TXF",
            contract="TX1",
            direction=Direction.LONG,
            status=PositionStatus.LONG,
            quantity=1,
        ),
    ]

    target = MultiStrategyDecisionLayer().decide(positions)

    assert target.quantity == 3
    assert [
        attribution.strategy_id
        for attribution in target.attributions
    ] == [
        "LONG-TERM",
        "SHORT-TERM",
    ]
    assert [
        attribution.quantity
        for attribution in target.attributions
    ] == [2, 1]
