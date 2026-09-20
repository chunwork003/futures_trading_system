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
    / "walk_forward_txf_1m.json"
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
    print("=== P7-2 Walk-Forward Optimization ===")
    print(f"Database : {DATABASE_PATH}")
    print("Symbol   : TXF")
    print()

    print("[1/4] Loading TXF 1m data...")

    bars = load_txf_1m()

    print(
        f"       rows={bars.height:,}, "
        f"first={bars['timestamp'][0]}, "
        f"last={bars['timestamp'][-1]}"
    )
    print()

    print("[2/4] WFO configuration...")
    print("       train=60,000 bars")
    print("       test =20,000 bars")
    print("       step =20,000 bars")
    print("       mode =rolling")
    print()

    backtest_config = BacktestConfig(
        symbol="TXF",
        timeframe="1m",
        initial_capital=1_000_000,
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

    print("[3/4] Running WFO...")
    results = optimizer.run(bars)

    print()
    print("[4/4] WFO Results")
    print()

    output = []

    for result in results:
        print(
            f"Window {result.window_id:02d} | "
            f"Train {result.train_start} -> {result.train_end} | "
            f"OOS {result.test_start} -> {result.test_end}"
        )

        print(
            f"  Selected : {result.selected_parameter_id}"
        )

        print(
            f"  Train    : "
            f"trades={result.train_trades:5d} "
            f"Exp={result.train_expectancy:9.2f} "
            f"PF={result.train_profit_factor:.4f} "
            f"DD={result.train_max_drawdown_pct:8.2%}"
        )

        print(
            f"  OOS      : "
            f"trades={result.oos_trades:5d} "
            f"Exp={result.oos_expectancy:9.2f} "
            f"PF={result.oos_profit_factor:.4f} "
            f"DD={result.oos_max_drawdown_pct:8.2%} "
            f"PnL={result.oos_net_profit:,.2f}"
        )

        print()

        output.append(
            {
                "window_id": result.window_id,
                "train_start": result.train_start.isoformat(),
                "train_end": result.train_end.isoformat(),
                "test_start": result.test_start.isoformat(),
                "test_end": result.test_end.isoformat(),
                "selected_parameter_id": result.selected_parameter_id,
                "selected_fast_window": result.selected_fast_window,
                "selected_slow_window": result.selected_slow_window,
                "train": {
                    "trades": result.train_trades,
                    "expectancy": result.train_expectancy,
                    "profit_factor": result.train_profit_factor,
                    "max_drawdown_pct": result.train_max_drawdown_pct,
                    "net_profit": result.train_net_profit,
                },
                "oos": {
                    "trades": result.oos_trades,
                    "expectancy": result.oos_expectancy,
                    "profit_factor": result.oos_profit_factor,
                    "max_drawdown_pct": result.oos_max_drawdown_pct,
                    "net_profit": result.oos_net_profit,
                    "final_equity": result.oos_final_equity,
                },
            }
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            {
                "symbol": "TXF",
                "timeframe": "1m",
                "train_size": 60_000,
                "test_size": 20_000,
                "step_size": 20_000,
                "expanding": False,
                "windows": output,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
