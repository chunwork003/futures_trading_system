from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import duckdb
import polars as pl

from backtest.engine import BacktestConfig
from backtest.oos import aggregate_oos_results
from backtest.optimization import OptimizationConstraint
from backtest.walk_forward import WalkForwardConfig
from backtest.walk_forward_optimization import (
    WalkForwardOptimizationConfig,
    WalkForwardOptimizer,
)


DATABASE_PATH = PROJECT_ROOT / "database" / "market.duckdb"

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "backtest_results"
    / "oos_txf_1m.json"
)


def load_txf_1m() -> pl.DataFrame:
    with duckdb.connect(str(DATABASE_PATH), read_only=True) as conn:
        table = conn.execute(
            """
            SELECT
                timestamp,
                trade_date,
                open,
                high,
                low,
                close,
                volume
            FROM txf_1m
            ORDER BY timestamp
            """
        ).to_arrow_table()

    return pl.from_arrow(table)


def main() -> None:
    print("=== P8 OOS Analysis ===")
    print(f"Database : {DATABASE_PATH}")
    print("Symbol   : TXF")

    bars = load_txf_1m()

    print(
        f"Rows     : {bars.height}"
    )

    backtest_config = BacktestConfig(
        initial_capital=1_000_000,
        symbol="TXF",
        timeframe="1m",
        quantity=1,
        multiplier=200,
        commission_per_contract=0.0,
        slippage_points=0.0,
    )

    wfo_config = WalkForwardOptimizationConfig(
        window_config=WalkForwardConfig(
            train_size=60_000,
            test_size=20_000,
            step_size=20_000,
            expanding=False,
        ),
        constraints=OptimizationConstraint(
            min_trades=100,
            min_profit_factor=1.0,
            max_drawdown_pct=-80.0,
        ),
    )

    optimizer = WalkForwardOptimizer(
        backtest_config=backtest_config,
        config=wfo_config,
    )

    print()
    print("[1/3] Running WFO...")
    results = optimizer.run(bars)

    print()
    print("[2/3] Aggregating OOS...")
    report = aggregate_oos_results(results)

    print()
    print("[3/3] OOS Results")
    print(f"  Windows             : {report.window_count}")
    print(f"  Total OOS trades    : {report.total_trades}")
    print(f"  Total OOS PnL       : {report.total_net_profit:,.2f}")
    print(f"  Positive windows    : {report.positive_windows}")
    print(f"  Negative windows    : {report.negative_windows}")
    print(
        "  Non-negative ratio  : "
        f"{report.non_negative_window_ratio:.2%}"
    )
    print(
        "  Avg OOS expectancy  : "
        f"{report.average_window_expectancy:.2f}"
    )
    print(
        "  Median expectancy   : "
        f"{report.median_window_expectancy:.2f}"
    )
    print(
        "  Avg OOS PF          : "
        f"{report.average_window_profit_factor:.4f}"
    )
    print(
        "  Median OOS PF       : "
        f"{report.median_window_profit_factor:.4f}"
    )
    print(
        "  Worst OOS PnL       : "
        f"{report.worst_window_net_profit:,.2f}"
    )
    print(
        "  Best OOS PnL        : "
        f"{report.best_window_net_profit:,.2f}"
    )
    print(
        "  Worst OOS DD        : "
        f"{report.worst_window_drawdown_pct:.2%}"
    )

    print()
    print("[Parameter Frequency]")

    for item in report.parameter_frequencies:
        print(
            f"  {item.parameter_id:<12} "
            f"{item.selected_windows} windows"
        )

    print()
    print("[Window Results]")

    for window in report.windows:
        print(
            f"  W{window.window_id}: "
            f"{window.parameter_id:<12} "
            f"Trades={window.trades:5d} "
            f"PF={window.profit_factor:.4f} "
            f"Exp={window.expectancy:8.2f} "
            f"DD={window.max_drawdown_pct:7.2%} "
            f"PnL={window.net_profit:10,.2f}"
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            report.to_dict(),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print(f"Report   : {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
