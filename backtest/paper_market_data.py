from __future__ import annotations

from typing import Any

from backtest.market_data import MarketDataProvider


class PaperMarketDataProvider(MarketDataProvider):
    def __init__(self, bars: list[dict[str, Any]]) -> None:
        self._bars = bars
        self._index = -1

    def get_latest(self) -> dict[str, Any]:
        if not self._bars:
            raise RuntimeError("No market data available.")

        return self._bars[-1]

    def get_next(self) -> dict[str, Any]:
        if not self._bars:
            raise RuntimeError("No market data available.")

        if self._index + 1 >= len(self._bars):
            raise RuntimeError("No next market data available.")

        self._index += 1
        return self._bars[self._index]

    def get_bars(self) -> list[dict[str, Any]]:
        return list(self._bars)
