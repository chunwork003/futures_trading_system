from backtest.paper_market_data import PaperMarketDataProvider


def test_get_latest_returns_last_bar():
    bars = [{"close": 20000}, {"close": 20010}]
    provider = PaperMarketDataProvider(bars)

    assert provider.get_latest() == {"close": 20010}


def test_get_bars_returns_copy():
    bars = [{"close": 20000}]
    provider = PaperMarketDataProvider(bars)

    result = provider.get_bars()
    result.append({"close": 20010})

    assert provider.get_bars() == [{"close": 20000}]


def test_get_latest_raises_when_empty():
    provider = PaperMarketDataProvider([])

    try:
        provider.get_latest()
    except RuntimeError as exc:
        assert str(exc) == "No market data available."
    else:
        raise AssertionError("Expected RuntimeError")
from datetime import datetime

import pytest

from backtest.paper_market_data import PaperMarketDataProvider


def test_get_next_returns_bars_in_order():
    bars = [
        {"timestamp": datetime(2026, 1, 5, 9, 0), "close": 20_000},
        {"timestamp": datetime(2026, 1, 5, 9, 1), "close": 20_100},
    ]

    provider = PaperMarketDataProvider(bars)

    assert provider.get_next() == bars[0]
    assert provider.get_next() == bars[1]


def test_get_next_raises_when_exhausted():
    provider = PaperMarketDataProvider(
        [{"timestamp": datetime(2026, 1, 5, 9, 0), "close": 20_000}]
    )

    provider.get_next()

    with pytest.raises(RuntimeError, match="No next market data available"):
        provider.get_next()
