import polars as pl

from ingestion.yahoo import YahooDataSource


def test_yahoo_source_name():
    source = YahooDataSource()

    assert source.source_name == "yahoo"


def test_yahoo_normalize_single_ticker():
    import pandas as pd

    index = pd.date_range(
        "2026-09-18 09:00",
        periods=2,
        freq="min",
        tz="Asia/Taipei",
    )

    frame = pd.DataFrame(
        {
            "Open": [47000.0, 47001.0],
            "High": [47005.0, 47006.0],
            "Low": [46995.0, 46996.0],
            "Close": [47002.0, 47004.0],
            "Volume": [100, 120],
        },
        index=index,
    )

    result = YahooDataSource._normalize(
        frame,
        canonical_symbol="TXF",
        yahoo_symbol="WTXV6",
        timeframe="1m",
        timezone="Asia/Taipei",
    )

    assert result.height == 2
    assert result.columns == [
        "timestamp",
        "trade_date",
        "symbol",
        "contract",
        "timeframe",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "session",
        "source",
    ]

    assert result["symbol"].unique().to_list() == ["TXF"]
    assert result["contract"].unique().to_list() == ["WTXV6"]
    assert result["source"].unique().to_list() == ["yahoo"]
    assert result["timeframe"].unique().to_list() == ["1m"]


def test_yahoo_normalize_empty():
    result = YahooDataSource._empty()

    assert result.height == 0
    assert "timestamp" in result.columns
    assert "close" in result.columns
