from datetime import datetime, timedelta

import polars as pl

from features.trend import trend_features
from strategies.trend_state import TrendStateStrategy


def test_feature_to_strategy_signal_flow():
    timestamps = [
        datetime(2026, 1, 5, 9, 0) + timedelta(minutes=i)
        for i in range(80)
    ]

    prices = [
        30000 + i * 5
        for i in range(80)
    ]

    bars = pl.DataFrame(
        {
            "timestamp": timestamps,
            "trade_date": [ts.date() for ts in timestamps],
            "symbol": ["TXF"] * 80,
            "contract": ["TXFR1"] * 80,
            "timeframe": ["1m"] * 80,
            "open": prices,
            "high": [p + 2 for p in prices],
            "low": [p - 2 for p in prices],
            "close": prices,
            "volume": [100] * 80,
        }
    )

    featured = trend_features(bars)

    assert "trend_state" in featured.columns

    strategy = TrendStateStrategy(
        symbol="TXF",
        timeframe="1m",
    )

    signals = []

    for row in featured.iter_rows(named=True):
        signals.extend(strategy.on_bar(row))

    assert len(signals) >= 1

    for signal in signals:
        assert signal.symbol == "TXF"
        assert signal.timeframe == "1m"
        assert signal.entry_type == "NEXT_BAR_OPEN"
