import pytest

from backtest.models import Direction
from backtest.strategy_attribution import StrategyAttribution
from backtest.strategy_attribution_aggregator import (
    StrategyAttributionAggregator,
)


def test_strategy_attribution_aggregator_rejects_direction_conflict():
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
            direction=Direction.SHORT,
            quantity=1,
        ),
    ]

    with pytest.raises(
        ValueError,
        match="conflicting attribution directions",
    ):
        StrategyAttributionAggregator().aggregate(attributions)
