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
OUTPUT_DIR = PROJECT_ROOT / "data" / "backtest_results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SYMBOL = "TXF"
TIMEFRAME = "1m"
INITIAL_CAPITAL = 1_000_000.0
QUANTITY = 1
MULTIPLIER = 200.0


def load_bars() -> pl.DataFrame:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"DuckDB not found: {DATABASE_PATH}"
        )

    conn = duckdb.connect(str(DATABASE_PATH))

    try:
        tables = conn.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name = 'txf_1m'
            """
        ).fetchall()

        views = conn.execute(
            """
            SELECT table_name
            FROM information_schema.views
            WHERE table_name = 'txf_1m'
            """
        ).fetchall()

        if not tables and not views:
            raise RuntimeError(
                "DuckDB view/table 'txf_1m' does not exist."
            )

        query = """
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
        """

        arrow_table = conn.execute(
            query,
            [SYMBOL],
        ).fetch_arrow_table()

        df = pl.from_arrow(arrow_table)

    finally:
        conn.close()

    if df.is_empty():
        raise RuntimeError(
            "No TXF bars found in txf_1m."
        )

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


def generate_signals(
    df: pl.DataFrame,
) -> list:
    strategy = TrendStateExitStrategy(
        symbol=SYMBOL,
        timeframe=TIMEFRAME,
        quantity=QUANTITY,
    )

    strategy.reset()

    signals = []

    for row in df.iter_rows(named=True):
        signals.extend(
            strategy.on_bar(row)
        )

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


def serialize_report(
    df: pl.DataFrame,
    signals: list,
    trades: list,
    report: PerformanceReport,
) -> dict:
    statistics = report.trade_statistics
    metrics = report.performance_metrics

    return {
        "backtest": {
            "symbol": SYMBOL,
            "timeframe": TIMEFRAME,
            "strategy_id": "TREND_STATE_EXIT",
            "strategy_version": "1.0.0",
            "initial_capital": INITIAL_CAPITAL,
            "quantity": QUANTITY,
            "multiplier": MULTIPLIER,
        },
        "data": {
            "rows": df.height,
            "first_timestamp": str(
                df["timestamp"][0]
            ),
            "last_timestamp": str(
                df["timestamp"][-1]
            ),
            "sources": sorted(
                {
                    str(value)
                    for value in
                    df["source"]
                    .drop_nulls()
                    .unique()
                    .to_list()
                }
            ),
        },
        "signals": {
            "total": len(signals),
        },
        "performance": {
            "total_trades": statistics.total_trades,
            "winning_trades": statistics.winning_trades,
            "losing_trades": statistics.losing_trades,
            "breakeven_trades": statistics.breakeven_trades,
            "win_rate": statistics.win_rate,
            "gross_profit": statistics.gross_profit,
            "gross_loss": statistics.gross_loss,
            "net_profit": statistics.net_profit,
            "average_trade": statistics.average_trade,
            "average_winner": statistics.average_winner,
            "average_loser": statistics.average_loser,
            "largest_winner": statistics.largest_winner,
            "largest_loser": statistics.largest_loser,
            "profit_factor": metrics.profit_factor,
            "expectancy": metrics.expectancy,
            "expectancy_r": metrics.expectancy_r,
            "final_equity": report.final_equity,
            "max_drawdown": report.max_drawdown,
            "max_drawdown_pct": report.max_drawdown_pct,
            "longest_drawdown_bars": (
                report.longest_drawdown_bars
            ),
            "longest_recovery_bars": (
                report.longest_recovery_bars
            ),
            "average_holding_minutes": (
                statistics.average_holding_minutes
            ),
            "average_r_multiple": (
                statistics.average_r_multiple
            ),
        },
        "trades": [
            trade.model_dump(mode="json")
            for trade in trades
        ],
    }


def main() -> None:
    print("=== P5 First Real Backtest ===")
    print(f"Database : {DATABASE_PATH}")
    print(f"Symbol   : {SYMBOL}")
    print("Strategy : TREND_STATE_EXIT v1.0.0")
    print()

    print("[1/5] Loading TXF 1m data...")
    df = load_bars()

    print(
        f"       rows={df.height:,}, "
        f"first={df['timestamp'][0]}, "
        f"last={df['timestamp'][-1]}"
    )

    print("[2/5] Building features...")
    df = build_features(df)

    print(
        "       trend_state="
        f"{df['trend_state'].value_counts().to_dict()}"
    )

    print("[3/5] Generating signals...")
    signals = generate_signals(df)

    print(
        f"       signals={len(signals):,}"
    )

    print("[4/5] Running backtest...")
    engine, trades, report = run_backtest(
        df,
        signals,
    )

    print(
        f"       trades={len(trades):,}"
    )

    print("[5/5] Writing report...")

    result = serialize_report(
        df,
        signals,
        trades,
        report,
    )

    output_path = (
        OUTPUT_DIR
        / "trend_state_txf_1m_first_backtest.json"
    )

    output_path.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    statistics = report.trade_statistics
    metrics = report.performance_metrics

    print()
    print("=== RESULT ===")
    print(
        f"Data rows          : {df.height:,}"
    )
    print(
        f"Signals            : {len(signals):,}"
    )
    print(
        f"Trades             : "
        f"{statistics.total_trades:,}"
    )
    print(
        f"Win rate           : "
        f"{statistics.win_rate:.2%}"
    )
    print(
        f"Net PnL            : "
        f"{statistics.net_profit:,.2f}"
    )
    print(
        f"Average trade      : "
        f"{statistics.average_trade:,.2f}"
    )
    print(
        f"Profit factor      : "
        f"{metrics.profit_factor:.4f}"
    )
    print(
        f"Expectancy         : "
        f"{metrics.expectancy:,.2f}"
    )
    print(
        f"Final equity       : "
        f"{report.final_equity:,.2f}"
    )
    print(
        f"Max drawdown       : "
        f"{report.max_drawdown:,.2f}"
    )
    print(
        f"Max drawdown %     : "
        f"{report.max_drawdown_pct:.2%}"
    )
    print(
        "Avg holding min    : "
        f"{statistics.average_holding_minutes}"
    )
    print()
    print(
        f"Report: {output_path}"
    )


if __name__ == "__main__":
    main()
