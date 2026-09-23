from __future__ import annotations

from datetime import date, datetime
from typing import Any

from backtest.market_data import MarketDataProvider
from backtest.market_data_models import MarketBar


class PaperMarketDataProvider(MarketDataProvider):
    def __init__(self, bars: list[dict[str, Any] | MarketBar]) -> None:
        self._bars = [
            bar if isinstance(bar, MarketBar) else self._to_market_bar(bar)
            for bar in bars
        ]
        self._index = -1

    @staticmethod
    def _to_market_bar(bar: dict[str, Any]) -> MarketBar:
        standard_fields = {
            "timestamp",
            "trade_date",
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "amount",
            "tick_count",
            "timeframe",
            "exchange",
            "contract",
            "session",
            "source",
        }

        return MarketBar(
            timestamp=bar.get("timestamp", datetime.min),
            trade_date=bar.get("trade_date", date.min),
            symbol=bar.get("symbol", ""),
            open=float(bar["open"]),
            high=float(bar["high"]),
            low=float(bar["low"]),
            close=float(bar["close"]),
            volume=int(bar["volume"]),
            amount=(
                float(bar["amount"])
                if bar.get("amount") is not None
                else None
            ),
            tick_count=(
                int(bar["tick_count"])
                if bar.get("tick_count") is not None
                else None
            ),
            timeframe=bar.get("timeframe"),
            exchange=bar.get("exchange"),
            contract=bar.get("contract"),
            session=bar.get("session"),
            source=bar.get("source"),
            data={
                key: value
                for key, value in bar.items()
                if key not in standard_fields
            },
        )

    def get_latest(self) -> MarketBar:
        if not self._bars:
            raise RuntimeError("No market data available.")

        return self._bars[-1]

    def get_next(self) -> MarketBar:
        if not self._bars:
            raise RuntimeError("No market data available.")

        if self._index + 1 >= len(self._bars):
            raise RuntimeError("No next market data available.")

        self._index += 1
        return self._bars[self._index]

    def get_bars(self) -> list[MarketBar]:
        return list(self._bars)
