import pytest

from backtest.decision_layer import MultiStrategyDecisionLayer
from backtest.models import Direction, PositionStatus
from backtest.strategy_position import StrategyVirtualPosition


def test_decision_layer_rejects_conflicting_strategy_directions():
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
            direction=Direction.SHORT,
            status=PositionStatus.SHORT,
            quantity=1,
        ),
    ]

    with pytest.raises(
        ValueError,
        match="conflicting strategy directions",
    ):
        MultiStrategyDecisionLayer().decide(positions)
