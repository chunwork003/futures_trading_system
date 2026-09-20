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
from backtest.optimization import (
    DEFAULT_PARAMETER_GRID,
    OptimizationConstraint,
    TrendParameterOptimizer,
)


DATABASE_PATH = PROJECT_ROOT / "database" / "market.duckdb"
OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "backtest_results"
    / "trend_state_parameter_optimization.json"
)

SYMBOL = "TXF"
TIMEFRAME = "1m"
INITIAL_CAPITAL = 1_000_000.0
QUANTITY = 1
MULTIPLIER = 200.0


def load_txf_1m() -> pl.DataFrame:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"DuckDB not found: {DATABASE_PATH}"
        )

    conn = duckdb.connect(
        str(DATABASE_PATH),
        read_only=True,
    )

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
        ).to_arrow_table()

        df = pl.from_arrow(arrow_table)

    finally:
        conn.close()

    if df.is_empty():
        raise RuntimeError(
            "No TXF bars found in txf_1m."
        )

    required_columns = {
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
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise RuntimeError(
            "Missing required columns: "
            f"{sorted(missing_columns)}"
        )

    return df


def main() -> None:
    print("=== P6 Parameter Optimization ===")
    print(f"Database : {DATABASE_PATH}")
    print(f"Symbol   : {SYMBOL}")
    print()

    print("[1/4] Loading TXF 1m data...")

    bars = load_txf_1m()

    print(
        f"       rows={bars.height:,}, "
        f"first={bars['timestamp'][0]}, "
        f"last={bars['timestamp'][-1]}"
    )

    print()
    print("[2/4] Parameter grid...")

    for params in DEFAULT_PARAMETER_GRID:
        baseline = (
            " [BASELINE]"
            if (
                params.fast_window == 20
                and params.slow_window == 60
            )
            else ""
        )

        print(
            f"       {params.parameter_id}"
            f"{baseline}"
        )

    print()
    print("[3/4] Running optimization...")

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

    constraints = OptimizationConstraint(
        min_trades=100,
        min_profit_factor=1.0,
        max_drawdown_pct=-80.0,
    )

    optimizer = TrendParameterOptimizer(
        backtest_config=config,
        constraints=constraints,
    )

    results = optimizer.run(bars)

    results.sort(
        key=lambda item: (
            item.passes_constraints,
            item.expectancy,
            item.profit_factor,
        ),
        reverse=True,
    )

    print()
    print("[4/4] Results")

    for index, result in enumerate(
        results,
        start=1,
    ):
        baseline = (
            " BASELINE"
            if result.is_baseline
            else ""
        )

        candidate = (
            " PASS"
            if result.passes_constraints
            else " FAIL"
        )

        print(
            f"{index:2d}. "
            f"{result.parameter_id:12s} "
            f"trades={result.total_trades:6d} "
            f"win={result.win_rate * 100:6.2f}% "
            f"PF={result.profit_factor:7.4f} "
            f"Exp={result.expectancy:9.2f} "
            f"DD={result.max_drawdown_pct:8.2%}"
            f"{candidate}"
            f"{baseline}"
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = {
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME,
        "data_rows": bars.height,
        "first_timestamp": str(
            bars["timestamp"][0]
        ),
        "last_timestamp": str(
            bars["timestamp"][-1]
        ),
        "baseline": "ema_20_60",
        "constraints": {
            "min_trades": constraints.min_trades,
            "min_profit_factor": (
                constraints.min_profit_factor
            ),
            "max_drawdown_pct": (
                constraints.max_drawdown_pct
            ),
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
                "passes_constraints": (
                    result.passes_constraints
                ),
            }
            for result in results
        ],
    }

    OUTPUT_PATH.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print(f"Report   : {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

