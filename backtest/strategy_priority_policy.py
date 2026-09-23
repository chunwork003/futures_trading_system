from __future__ import annotations

from collections.abc import Iterable

from backtest.models import Direction
from backtest.strategy_conflict_policy import StrategyConflictPolicy
from backtest.strategy_position import StrategyVirtualPosition


class PriorityStrategyConflictPolicy(StrategyConflictPolicy):
    def resolve(
        self,
        positions: Iterable[StrategyVirtualPosition],
    ) -> Direction:
        positions = list(positions)

        if not positions:
            raise ValueError("at least one strategy position is required")

        highest_priority = max(
            position.priority
            for position in positions
        )

        highest_priority_positions = [
            position
            for position in positions
            if position.priority == highest_priority
        ]

        directions = {
            position.direction
            for position in highest_priority_positions
        }

        if len(directions) > 1:
            raise ValueError(
                "equal priority conflict requires explicit resolution"
            )

        return highest_priority_positions[0].direction
