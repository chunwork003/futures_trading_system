from datetime import date, datetime

from backtest.market_data_models import MarketBar


def test_market_bar_stores_standard_market_data():
    bar = MarketBar(
        timestamp=datetime(2026, 1, 5, 9, 0),
        trade_date=date(2026, 1, 5),
        symbol="TXF",
        close=20000.0,
    )

    assert bar.timestamp == datetime(2026, 1, 5, 9, 0)
    assert bar.trade_date == date(2026, 1, 5)
    assert bar.symbol == "TXF"
    assert bar.close == 20000.0
