from backtest.models import Direction
from backtest.strategy_attribution import StrategyAttribution
from backtest.strategy_attribution_aggregator import (
    StrategyAttributionAggregator,
)


def test_strategy_attribution_aggregator_combines_same_direction():
    attributions = [
        StrategyAttribution(
            strategy_id="LONG-TERM",
            symbol="TXF",
            contract="TX1",
            direction=Direction.LONG,
            quantity=2,
        ),
        StrategyAttribution(
            strategy_id="SHORT-TERM",
            symbol="TXF",
            contract="TX1",
            direction=Direction.LONG,
            quantity=1,
        ),
    ]

    target = StrategyAttributionAggregator().aggregate(attributions)

    assert target.symbol == "TXF"
    assert target.contract == "TX1"
    assert target.direction == Direction.LONG
    assert target.quantity == 3
