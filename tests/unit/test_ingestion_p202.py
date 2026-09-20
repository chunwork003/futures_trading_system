from datetime import date

import polars as pl

from ingestion.canonical import (
    filter_date_range,
    validate_canonical_bars,
)
from ingestion.github_txf_parser import parse_txf_sql


def test_parse_txf_sql(tmp_path):
    sql = """
COPY futures_1min (datetime, product_id, open, high, low, close, volume, trading_date, is_synthetic) FROM stdin;
2026-01-02 08:45:00    TXFR1    100.00    101.00    99.00    100.50    10    2026-01-02    f
2026-01-02 08:46:00    TXFR1    100.50    102.00    100.00    101.50    20    2026-01-02    f
\\.
"""

    path = tmp_path / "data_TXFR1_2026.sql"
    path.write_text(sql, encoding="utf-8")

    df = parse_txf_sql(path)

    assert df.height == 2
    assert df.columns == [
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

    assert df["symbol"][0] == "TXF"
    assert df["contract"][0] == "TXFR1"
    assert df["timeframe"][0] == "1m"
    assert df["open"][0] == 100.0
    assert df["high"][1] == 102.0
    assert df["volume"][1] == 20


def test_filter_date_range():
    df = pl.DataFrame(
        {
            "trade_date": [
                date(2026, 1, 1),
                date(2026, 1, 2),
                date(2026, 1, 3),
            ],
            "value": [1, 2, 3],
        }
    )

    result = filter_date_range(
        df,
        date(2026, 1, 2),
        date(2026, 1, 2),
    )

    assert result.height == 1
    assert result["value"][0] == 2


def test_validate_canonical_bars(tmp_path):
    sql = """
COPY futures_1min (datetime, product_id, open, high, low, close, volume, trading_date, is_synthetic) FROM stdin;
2026-01-02 08:45:00    TXFR1    100.00    101.00    99.00    100.50    10    2026-01-02    f
\\.
"""

    path = tmp_path / "data_TXFR1_2026.sql"
    path.write_text(sql, encoding="utf-8")

    df = parse_txf_sql(path)

    validate_canonical_bars(df)
