from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import duckdb
import polars as pl

from analysis.performance_report import PerformanceReport
from backtest.engine import BacktestEngine
from backtest.models import BacktestConfig
from features.builder import FeatureBuilder
from features.trend import trend_features
from strategies.trend_state_exit import TrendStateExitStrategy


DATABASE_PATH = PROJECT_ROOT / "database" / "market.duckdb"
OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "backtest_results"
    / "multi_strategy_txf_1m.json"
)

SYMBOL = "TXF"
TIMEFRAME = "1m"
INITIAL_CAPITAL = 1_000_000.0
QUANTITY = 1
MULTIPLIER = 200.0


def load_bars() -> pl.DataFrame:
    connection = duckdb.connect(str(DATABASE_PATH), read_only=True)

    try:
        table = connection.execute(
            """
            SELECT
                timestamp,
                trade_date,
                symbol,
                contract,
                timeframe,
                open,
                high,
                low,
                close,
                volume,
                session,
                source
            FROM txf_1m
            WHERE symbol = ?
            ORDER BY timestamp
            """,
            [SYMBOL],
        ).fetch_arrow_table()
    finally:
        connection.close()

    df = pl.from_arrow(table)

    if df.is_empty():
        raise RuntimeError("No TXF bars found in txf_1m.")

    return df


def build_features(df: pl.DataFrame) -> pl.DataFrame:
    builder = FeatureBuilder()

    result = builder.build(df)
    result = trend_features(result)

    if "trend_state" not in result.columns:
        raise RuntimeError(
            "Trend feature generation did not produce trend_state."
        )

    return result


def generate_signals(df: pl.DataFrame) -> list:
    strategy = TrendStateExitStrategy(
        symbol=SYMBOL,
        timeframe=TIMEFRAME,
        quantity=QUANTITY,
    )

    strategy.reset()

    signals = []

    for row in df.iter_rows(named=True):
        signals.extend(strategy.on_bar(row))

    return signals


def run_backtest(
    df: pl.DataFrame,
    signals: list,
):
    config = BacktestConfig(
        initial_capital=INITIAL_CAPITAL,
        symbol=SYMBOL,
        timeframe=TIMEFRAME,
        quantity=QUANTITY,
        multiplier=MULTIPLIER,
        commission_per_contract=0.0,
        slippage_points=0.0,
        allow_multiple_positions=False,
        intrabar_priority="SL_FIRST",
        end_of_data_exit=True,
    )

    engine = BacktestEngine(config)

    trades = engine.run(
        bars=df.iter_rows(named=True),
        signals=signals,
    )

    report = PerformanceReport.from_trades(
        trades,
        engine.equity_curve,
    )

    return engine, trades, report


def main() -> None:
    raw_df = load_bars()
    df = build_features(raw_df)
    signals = generate_signals(df)
    engine, trades, report = run_backtest(df, signals)

    stats = report.trade_statistics
    metrics = report.performance_metrics

    output = {
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME,
        "bar_count": df.height,
        "strategies": [
            {
                "strategy_id": "TREND_STATE_EXIT",
                "version": "1.0.0",
                "signal_count": len(signals),
                "trade_statistics": stats.__dict__,
                "performance_metrics": metrics.__dict__,
                "final_equity": report.final_equity,
                "max_drawdown": report.max_drawdown,
                "max_drawdown_pct": report.max_drawdown_pct,
                "longest_drawdown_bars": report.longest_drawdown_bars,
                "longest_recovery_bars": report.longest_recovery_bars,
            }
        ],
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_PATH.write_text(
        json.dumps(
            output,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print("=== P10-2 Multi-Strategy Backtest ===")
    print(f"Bars       : {df.height}")
    print()
    print("[TREND_STATE_EXIT]")
    print(f"Signals    : {len(signals)}")
    print(f"Trades     : {stats.total_trades}")
    print(f"Win rate   : {stats.win_rate:.2%}")
    print(f"Net PnL    : {stats.net_profit:,.2f}")
    print(f"PF         : {metrics.profit_factor:.4f}")
    print(f"Expectancy : {metrics.expectancy:,.2f}")
    print(f"Final Eq.  : {report.final_equity:,.2f}")
    print(f"Max DD     : {report.max_drawdown:,.2f}")
    print(f"Max DD %   : {report.max_drawdown_pct:.2%}")
    print()
    print(f"Report     : {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
