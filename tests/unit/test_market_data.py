from datetime import date, datetime

from backtest.market_data_models import MarketBar


def test_market_bar_stores_standard_ohlcv_data():
    bar = MarketBar(
        timestamp=datetime(2026, 1, 5, 9, 0),
        trade_date=date(2026, 1, 5),
        symbol="TXF",
        open=20000.0,
        high=20050.0,
        low=19980.0,
        close=20030.0,
        volume=1250,
        amount=25037500.0,
    )

    assert bar.timestamp == datetime(2026, 1, 5, 9, 0)
    assert bar.trade_date == date(2026, 1, 5)
    assert bar.symbol == "TXF"
    assert bar.open == 20000.0
    assert bar.high == 20050.0
    assert bar.low == 19980.0
    assert bar.close == 20030.0
    assert bar.volume == 1250
    assert bar.amount == 25037500.0
