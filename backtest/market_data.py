from __future__ import annotations

from abc import ABC, abstractmethod

from backtest.market_data_models import MarketBar


class MarketDataProvider(ABC):
    @abstractmethod
    def get_latest(self) -> MarketBar:
        raise NotImplementedError

    @abstractmethod
    def get_next(self) -> MarketBar:
        raise NotImplementedError

    @abstractmethod
    def get_bars(self) -> list[MarketBar]:
        raise NotImplementedError
