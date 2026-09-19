from datetime import date, datetime

import polars as pl

from cleaning.validator import DataValidator


def create_valid_tick_dataframe() -> pl.DataFrame:

    return pl.DataFrame(
        {
            "timestamp": [
                datetime(2026, 9, 15, 9, 0),
                datetime(2026, 9, 15, 9, 1),
            ],
            "trade_date": [
                date(2026, 9, 15),
                date(2026, 9, 15),
            ],
            "symbol": [
                "TXF",
                "TXF",
            ],
            "contract": [
                "TXF202609",
                "TXF202609",
            ],
            "price": [
                26000.0,
                26005.0,
            ],
            "volume": [
                10,
                15,
            ],
            "session": [
                "DAY",
                "DAY",
            ],
        }
    )


def test_valid_tick():

    df = create_valid_tick_dataframe()

    validator = DataValidator()

    result = validator.validate(df)

    assert result.valid is True
    assert len(result.errors) == 0


def test_missing_required_column():

    df = create_valid_tick_dataframe()

    df = df.drop("price")

    validator = DataValidator()

    result = validator.validate(df)

    assert result.valid is False
    assert any(
        "price" in error
        for error in result.errors
    )


def test_invalid_symbol():

    df = create_valid_tick_dataframe()

    df = df.with_columns(
        pl.lit("INVALID").alias("symbol")
    )

    validator = DataValidator()

    result = validator.validate(df)

    assert result.valid is False


def test_negative_price():

    df = create_valid_tick_dataframe()

    df = df.with_columns(
        pl.lit(-100.0).alias("price")
    )

    validator = DataValidator()

    result = validator.validate(df)

    assert result.valid is False


def test_negative_volume():

    df = create_valid_tick_dataframe()

    df = df.with_columns(
        pl.lit(-1).alias("volume")
    )

    validator = DataValidator()

    result = validator.validate(df)

    assert result.valid is False


def test_invalid_session():

    df = create_valid_tick_dataframe()

    df = df.with_columns(
        pl.lit("INVALID").alias("session")
    )

    validator = DataValidator()

    result = validator.validate(df)

    assert result.valid is False


def test_unsorted_timestamp():

    df = create_valid_tick_dataframe()

    df = df.sort(
        "timestamp",
        descending=True,
    )

    validator = DataValidator()

    result = validator.validate(df)

    assert result.valid is True
    assert any(
        "not sorted" in warning
        for warning in result.warnings
    )

def test_invalid_ohlc():

    df = pl.DataFrame(
        {
            "timestamp": [
                datetime(2026, 9, 15, 9, 0),
            ],
            "trade_date": [
                date(2026, 9, 15),
            ],
            "symbol": [
                "TXF",
            ],
            "price": [
                26000.0,
            ],
            "volume": [
                10,
            ],
            "open": [
                26000.0,
            ],
            "high": [
                25900.0,
            ],
            "low": [
                25800.0,
            ],
            "close": [
                25950.0,
            ],
        }
    )

    validator = DataValidator()

    result = validator.validate(df)

    assert result.valid is False
    assert any(
        "OHLC" in error
        for error in result.errors
    )