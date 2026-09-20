from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import duckdb
import polars as pl

from backtest.optimization import (
    DEFAULT_PARAMETER_GRID,
    TrendParameterOptimizer,
)


DATABASE_PATH = PROJECT_ROOT / "database" / "market.duckdb"
OUTPUT_DIR = PROJECT_ROOT / "data" / "backtest_results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SYMBOL = "TXF"


def load_bars() -> pl.DataFrame:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"DuckDB not found: {DATABASE_PATH}"
        )

    conn = duckdb.connect(str(DATABASE_PATH))

    try:
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
        ).to_arrow_table()

        df = pl.from_arrow(arrow_table)

    finally:
        conn.close()

    if df.is_empty():
        raise RuntimeError(
            "No TXF bars found in txf_1m."
        )

    return df


def serialize_results(
    df: pl.DataFrame,
    results: list,
) -> dict:
    return {
        "optimization": {
            "symbol": SYMBOL,
            "timeframe": "1m",
            "objective": "expectancy",
            "parameter_count": len(results),
            "baseline": "ema_20_60",
        },
        "data": {
            "rows": df.height,
            "first_timestamp": str(df["timestamp"][0]),
            "last_timestamp": str(df["timestamp"][-1]),
        },
        "results": [
            {
                "parameter_id": result.parameter_id,
                "fast_window": result.fast_window,
                "slow_window": result.slow_window,
                "total_trades": result.total_trades,
                "win_rate": result.win_rate,
                "net_profit": result.net_profit,
                "average_trade": result.average_trade,
                "profit_factor": result.profit_factor,
                "expectancy": result.expectancy,
                "max_drawdown": result.max_drawdown,
                "max_drawdown_pct": result.max_drawdown_pct,
                "final_equity": result.final_equity,
                "is_baseline": result.is_baseline,
            }
            for result in results
        ],
    }


def main() -> None:
    print("=== P6 Parameter Optimization ===")
    print(f"Database : {DATABASE_PATH}")
    print(f"Symbol   : {SYMBOL}")
    print()

    print("[1/4] Loading TXF 1m data...")

    df = load_bars()

    print(
        f"       rows={df.height:,}, "
        f"first={df['timestamp'][0]}, "
        f"last={df['timestamp'][-1]}"
    )

    print("[2/4] Parameter grid...")

    for parameter in DEFAULT_PARAMETER_GRID:
        baseline = " [BASELINE]" if (
            parameter.fast_window == 20
            and parameter.slow_window == 60
        ) else ""

        print(
            f"       {parameter.parameter_id}"
            f"{baseline}"
        )

    print()
    print("[3/4] Running parameter optimization...")

    optimizer = TrendParameterOptimizer(
        symbol=SYMBOL,
        timeframe="1m",
        initial_capital=1_000_000.0,
        quantity=1,
        multiplier=200.0,
    )

    results = optimizer.run(
        df,
        DEFAULT_PARAMETER_GRID,
    )

    print()
    print("[4/4] Results")

    ranked = sorted(
        results,
        key=lambda result: result.expectancy,
        reverse=True,
    )

    for index, result in enumerate(ranked, start=1):
        baseline = " BASELINE" if result.is_baseline else ""

        print(
            f"{index:>2}. "
            f"{result.parameter_id:<12} "
            f"trades={result.total_trades:>6,} "
            f"win={result.win_rate:>7.2%} "
            f"PF={result.profit_factor:>7.4f} "
            f"Exp={result.expectancy:>9.2f} "
            f"DD={result.max_drawdown_pct:>8.2%}"
            f"{baseline}"
        )

    output_path = (
        OUTPUT_DIR
        / "trend_state_parameter_optimization.json"
    )

    output_path.write_text(
        json.dumps(
            serialize_results(df, results),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print(f"Report: {output_path}")


if __name__ == "__main__":
    main()
