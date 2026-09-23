from __future__ import annotations

from collections.abc import Iterable

from backtest.models import Direction
from backtest.strategy_attribution import StrategyAttribution
from backtest.target_position import TargetAccountPosition


class StrategyAttributionAggregator:
    def aggregate(
        self,
        attributions: Iterable[StrategyAttribution],
    ) -> TargetAccountPosition:
        attributions = list(attributions)

        if not attributions:
            raise ValueError("at least one attribution is required")

        first = attributions[0]

        for attribution in attributions[1:]:
            if attribution.symbol != first.symbol:
                raise ValueError(
                    "all attributions must use the same symbol"
                )
            if attribution.contract != first.contract:
                raise ValueError(
                    "all attributions must use the same contract"
                )
            if attribution.direction != first.direction:
                raise ValueError(
                    "conflicting attribution directions require resolution"
                )

        return TargetAccountPosition(
            symbol=first.symbol,
            contract=first.contract,
            direction=first.direction,
            quantity=sum(
                attribution.quantity
                for attribution in attributions
            ),
        )
