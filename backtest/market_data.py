from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class MarketDataProvider(ABC):
    @abstractmethod
    def get_latest(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_bars(self) -> list[dict[str, Any]]:
        raise NotImplementedError
