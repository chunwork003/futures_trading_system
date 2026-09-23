from __future__ import annotations

from collections.abc import Iterable

from backtest.models import Direction
from backtest.strategy_conflict import StrategyConflict
from backtest.strategy_position import StrategyVirtualPosition


class StrategyConflictResolver:
    def detect(
        self,
        positions: Iterable[StrategyVirtualPosition],
    ) -> StrategyConflict | None:
        positions = list(positions)

        if not positions:
            return None

        directions = {position.direction for position in positions}

        if len(directions) <= 1:
            return None

        first = positions[0]

        return StrategyConflict(
            symbol=first.symbol,
            contract=first.contract,
            strategy_ids=[position.strategy_id for position in positions],
        )
