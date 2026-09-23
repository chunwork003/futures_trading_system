import pytest

from backtest.decision_layer import MultiStrategyDecisionLayer
from backtest.models import Direction, PositionStatus
from backtest.strategy_position import StrategyVirtualPosition


def make_position(
    strategy_id: str,
    symbol: str = "TXF",
    contract: str = "TX1",
    direction: Direction = Direction.LONG,
    quantity: int = 1,
) -> StrategyVirtualPosition:
    status = (
        PositionStatus.LONG
        if direction == Direction.LONG
        else PositionStatus.SHORT
    )

    return StrategyVirtualPosition(
        strategy_id=strategy_id,
        symbol=symbol,
        contract=contract,
        direction=direction,
        status=status,
        quantity=quantity,
    )


def test_decision_layer_rejects_empty_positions():
    with pytest.raises(ValueError, match="at least one"):
        MultiStrategyDecisionLayer().decide([])


def test_decision_layer_rejects_different_symbols():
    positions = [
        make_position("trend", symbol="TXF"),
        make_position("short_term", symbol="MTX"),
    ]

    with pytest.raises(ValueError, match="same symbol"):
        MultiStrategyDecisionLayer().decide(positions)


def test_decision_layer_rejects_conflicting_directions():
    positions = [
        make_position("trend", direction=Direction.LONG),
        make_position("short_term", direction=Direction.SHORT),
    ]

    with pytest.raises(ValueError, match="conflicting"):
        MultiStrategyDecisionLayer().decide(positions)
