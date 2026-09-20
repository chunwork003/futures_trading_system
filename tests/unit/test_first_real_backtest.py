from datetime import date, datetime, timedelta

import polars as pl

from analysis.performance_report import PerformanceReport
from backtest.engine import BacktestEngine
from backtest.models import BacktestConfig
from features.builder import FeatureBuilder
from features.trend import trend_features
from strategies.trend_state import TrendStateStrategy


def _make_bars() -> pl.DataFrame:
    start = datetime(2026, 1, 2, 9, 0)

    rows = []
    price = 20_000.0

    for index in range(100):
        timestamp = start + timedelta(minutes=index)

        if index < 30:
            price += 0.5
        else:
            price += 2.0

        rows.append(
            {
                "timestamp": timestamp,
                "trade_date": date(2026, 1, 2),
                "symbol": "TXF",
                "contract": "TXFR1",
                "timeframe": "1m",
                "open": price - 1.0,
                "high": price + 2.0,
                "low": price - 2.0,
                "close": price,
                "volume": 100,
                "session": "DAY",
                "source": "test",
            }
        )

    return pl.DataFrame(rows)


def test_first_backtest_pipeline() -> None:
    bars = _make_bars()

    features = FeatureBuilder().build(bars)

    assert features.height == bars.height
    assert "ema_20" in features.columns
    assert "ema_60" in features.columns

    features = trend_features(features)

    assert "trend_state" in features.columns
    assert features.height == bars.height

    strategy = TrendStateStrategy(
        symbol="TXF",
        timeframe="1m",
        quantity=1,
    )

    signals = []

    for row in features.iter_rows(named=True):
        signals.extend(strategy.on_bar(row))

    assert signals

    config = BacktestConfig(
        initial_capital=1_000_000,
        symbol="TXF",
        timeframe="1m",
        quantity=1,
        multiplier=200,
        commission_per_contract=0,
        slippage_points=0,
        end_of_data_exit=True,
    )

    engine = BacktestEngine(config)

    trades = engine.run(
        bars=features.iter_rows(named=True),
        signals=signals,
    )

    report = PerformanceReport.from_trades(
        trades,
        engine.equity_curve,
    )

    assert trades
    assert report.trade_statistics.total_trades == len(trades)
    assert report.final_equity is not None
    assert engine.equity_curve.snapshots
