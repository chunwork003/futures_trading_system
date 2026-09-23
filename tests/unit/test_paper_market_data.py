from datetime import date, datetime

import pytest

from backtest.market_data_models import MarketBar
from backtest.paper_market_data import PaperMarketDataProvider


def make_bar(close: float, minute: int = 0) -> MarketBar:
    return MarketBar(
        timestamp=datetime(2026, 1, 5, 9, minute),
        trade_date=date(2026, 1, 5),
        symbol="TXF",
        open=close - 10,
        high=close + 20,
        low=close - 30,
        close=close,
        volume=1000 + minute,
        amount=close * (1000 + minute),
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


def test_dict_is_converted_to_market_bar_with_ohlcv():
    provider = PaperMarketDataProvider(
        [
            {
                "timestamp": datetime(2026, 1, 5, 9, 0),
                "trade_date": date(2026, 1, 5),
                "symbol": "TXF",
                "open": 20000.0,
                "high": 20050.0,
                "low": 19980.0,
                "close": 20030.0,
                "volume": 1250,
                "amount": 25037500.0,
            }
        ]
    )

    result = provider.get_next()

    assert result.open == 20000.0
    assert result.high == 20050.0
    assert result.low == 19980.0
    assert result.close == 20030.0
    assert result.volume == 1250
    assert result.amount == 25037500.0


def test_dict_without_amount_keeps_amount_optional():
    provider = PaperMarketDataProvider(
        [
            {
                "timestamp": datetime(2026, 1, 5, 9, 0),
                "trade_date": date(2026, 1, 5),
                "symbol": "TXF",
                "open": 20000.0,
                "high": 20050.0,
                "low": 19980.0,
                "close": 20030.0,
                "volume": 1250,
            }
        ]
    )

    result = provider.get_next()

    assert result.volume == 1250
    assert result.amount is None
