from __future__ import annotations

from datetime import datetime, timedelta

import polars as pl
import pytest

from backtest.optimization import (
    DEFAULT_PARAMETER_GRID,
    TrendParameterOptimizer,
    TrendParameterSet,
)


def test_parameter_set_id() -> None:
    parameter = TrendParameterSet(
        fast_window=20,
        slow_window=60,
    )

    assert parameter.parameter_id == "ema_20_60"


def test_parameter_grid_contains_baseline() -> None:
    ids = {
        parameter.parameter_id
        for parameter in DEFAULT_PARAMETER_GRID
    }

    assert "ema_20_60" in ids


def test_parameter_grid_fast_is_smaller_than_slow() -> None:
    for parameter in DEFAULT_PARAMETER_GRID:
        assert parameter.fast_window < parameter.slow_window


def test_optimizer_returns_one_result_per_parameter() -> None:
    start = datetime(2026, 1, 1)

    rows = []

    for index in range(120):
        price = 20_000.0 + index * 2.0

        rows.append(
            {
                "timestamp": start + timedelta(minutes=index),
                "trade_date": (start + timedelta(minutes=index)).date(),
                "symbol": "TXF",
                "contract": "TXF202601",
                "timeframe": "1m",
                "open": price,
                "high": price + 2.0,
                "low": price - 2.0,
                "close": price + 1.0,
                "volume": 1,
                "session": "DAY",
                "source": "TEST",
            }
        )

    df = pl.DataFrame(rows)

    parameters = [
        TrendParameterSet(5, 10),
        TrendParameterSet(10, 20),
    ]

    optimizer = TrendParameterOptimizer(
        symbol="TXF",
        timeframe="1m",
    )

    results = optimizer.run(
        df,
        parameters,
    )

    assert len(results) == 2
    assert {
        result.parameter_id
        for result in results
    } == {
        "ema_5_10",
        "ema_10_20",
    }

    for result in results:
        assert result.total_trades >= 0
        assert result.final_equity >= 0
        assert result.parameter_id in {
            "ema_5_10",
            "ema_10_20",
        }


def test_optimizer_rejects_invalid_trend_parameters() -> None:
    start = datetime(2026, 1, 1)

    df = pl.DataFrame(
        {
            "timestamp": [start, start + timedelta(minutes=1)],
            "trade_date": [
                start.date(),
                start.date(),
            ],
            "symbol": ["TXF", "TXF"],
            "contract": ["TXF202601", "TXF202601"],
            "timeframe": ["1m", "1m"],
            "open": [20_000.0, 20_001.0],
            "high": [20_002.0, 20_003.0],
            "low": [19_998.0, 19_999.0],
            "close": [20_001.0, 20_002.0],
            "volume": [1, 1],
            "session": ["DAY", "DAY"],
            "source": ["TEST", "TEST"],
        }
    )

    optimizer = TrendParameterOptimizer()

    with pytest.raises(ValueError):
        optimizer.run(
            df,
            [TrendParameterSet(20, 10)],
        )
