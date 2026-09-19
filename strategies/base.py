from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from backtest.models import Signal


class Strategy(ABC):
    strategy_id: str
    strategy_version: str

    @abstractmethod
    def on_bar(self, row: dict[str, Any]) -> list[Signal]:
        """
        Process one completed bar and return zero or more signals.

        Strategy decisions must use only information available
        on the current completed bar and earlier bars.
        """
        raise NotImplementedError
