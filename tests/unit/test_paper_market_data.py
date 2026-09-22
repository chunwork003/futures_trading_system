from datetime import date, datetime

import pytest

from backtest.market_data_models import MarketBar
from backtest.paper_market_data import PaperMarketDataProvider


def make_bar(close: float, minute: int = 0) -> MarketBar:
    return MarketBar(
        timestamp=datetime(2026, 1, 5, 9, minute),
        trade_date=date(2026, 1, 5),
        symbol="TXF",
        close=close,
    )


def test_get_latest_returns_last_bar():
    bars = [make_bar(20000), make_bar(20010, 1)]
    provider = PaperMarketDataProvider(bars)

    assert provider.get_latest() == bars[-1]


def test_get_bars_returns_copy():
    bars = [make_bar(20000)]
    provider = PaperMarketDataProvider(bars)

    result = provider.get_bars()
    result.append(make_bar(20010, 1))

    assert provider.get_bars() == bars


def test_get_latest_raises_when_empty():
    provider = PaperMarketDataProvider([])

    with pytest.raises(RuntimeError, match="No market data available"):
        provider.get_latest()


def test_get_next_returns_bars_in_order():
    bars = [
        make_bar(20000),
        make_bar(20100, 1),
    ]

    provider = PaperMarketDataProvider(bars)

    assert provider.get_next() == bars[0]
    assert provider.get_next() == bars[1]


def test_get_next_raises_when_exhausted():
    provider = PaperMarketDataProvider([make_bar(20000)])

    provider.get_next()

    with pytest.raises(RuntimeError, match="No next market data available"):
        provider.get_next()


def test_get_next_returns_market_bar():
    bars = [make_bar(20000)]
    provider = PaperMarketDataProvider(bars)

    result = provider.get_next()

    assert isinstance(result, MarketBar)
    assert result == bars[0]
