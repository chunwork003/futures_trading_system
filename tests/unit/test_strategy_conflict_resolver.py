from backtest.models import Direction, PositionStatus
from backtest.strategy_conflict_resolver import StrategyConflictResolver
from backtest.strategy_position import StrategyVirtualPosition


def test_conflict_resolver_returns_none_when_strategies_agree():
    positions = [
        StrategyVirtualPosition(
            strategy_id="A",
            symbol="TXF",
            contract="TX1",
            direction=Direction.LONG,
            status=PositionStatus.LONG,
            quantity=1,
        ),
        StrategyVirtualPosition(
            strategy_id="B",
            symbol="TXF",
            contract="TX1",
            direction=Direction.LONG,
            status=PositionStatus.LONG,
            quantity=2,
        ),
    ]

    assert StrategyConflictResolver().detect(positions) is None


def test_conflict_resolver_detects_opposite_strategy_directions():
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

    conflict = StrategyConflictResolver().detect(positions)

    assert conflict is not None
    assert conflict.symbol == "TXF"
    assert conflict.contract == "TX1"
    assert conflict.strategy_ids == ["LONG-TERM", "SHORT-TERM"]
