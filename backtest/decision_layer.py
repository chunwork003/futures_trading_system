from __future__ import annotations

from collections.abc import Iterable

from backtest.models import Direction
from backtest.strategy_position import StrategyVirtualPosition
from backtest.target_position import TargetAccountPosition


class MultiStrategyDecisionLayer:
    def decide(
        self,
        positions: Iterable[StrategyVirtualPosition],
    ) -> TargetAccountPosition:
        positions = list(positions)

        if not positions:
            raise ValueError("at least one strategy position is required")

        first = positions[0]

        for position in positions[1:]:
            if position.symbol != first.symbol:
                raise ValueError("all strategy positions must use the same symbol")

            if position.contract != first.contract:
                raise ValueError(
                    "all strategy positions must use the same contract"
                )

            if position.direction != first.direction:
                raise ValueError(
                    "conflicting strategy directions require conflict resolution"
                )

        return TargetAccountPosition(
            symbol=first.symbol,
            contract=first.contract,
            direction=first.direction,
            quantity=sum(position.quantity for position in positions),
        )
