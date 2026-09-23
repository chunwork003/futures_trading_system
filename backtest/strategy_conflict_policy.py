from __future__ import annotations

from collections.abc import Iterable

from backtest.models import Direction
from backtest.strategy_position import StrategyVirtualPosition


class StrategyConflictPolicy:
    def resolve(
        self,
        positions: Iterable[StrategyVirtualPosition],
    ) -> Direction | None:
        raise NotImplementedError
