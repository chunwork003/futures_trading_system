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
from backtest.monte_carlo import MonteCarloMode, run_monte_carlo
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
    / "monte_carlo_oos_txf_1m.json"
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


def build_optimizer() -> WalkForwardOptimizer:
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

    return WalkForwardOptimizer(
        backtest_config=backtest_config,
        config=wfo_config,
    )


def build_report(
    shuffle_report,
    bootstrap_report,
    oos_results,
    trade_pnls,
) -> dict:
    return {
        "symbol": "TXF",
        "timeframe": "1m",
        "source": "actual_wfo_oos_trades",
        "wfo": {
            "window_count": len(oos_results),
            "trade_count": len(trade_pnls),
            "total_net_profit": sum(
                result.oos_net_profit
                for result in oos_results
            ),
        },
        "trade_pnl": {
            "trade_count": len(trade_pnls),
            "total_net_profit": sum(trade_pnls),
        },
        "shuffle": shuffle_report.to_dict(),
        "bootstrap": bootstrap_report.to_dict(),
    }


def main() -> None:
    print("=== P9-2 OOS Trade Monte Carlo ===")
    print(f"Database : {DATABASE_PATH}")
    print("Symbol   : TXF")
    print("Timeframe: 1m")

    bars = load_txf_1m()

    print(f"Rows     : {bars.height}")

    optimizer = build_optimizer()

    print()
    print("[1/4] Running WFO with actual OOS trades...")

    detailed_run = optimizer.run_with_trades(bars)

    oos_results = detailed_run.results
    oos_trades = detailed_run.oos_trades

    trade_pnls = [
        float(trade.net_pnl or 0.0)
        for trade in oos_trades
    ]

    window_trade_count = sum(
        result.oos_trades
        for result in oos_results
    )

    window_net_profit = sum(
        result.oos_net_profit
        for result in oos_results
    )

    trade_net_profit = sum(trade_pnls)

    if len(trade_pnls) != window_trade_count:
        raise RuntimeError(
            "OOS trade count mismatch: "
            f"trade records={len(trade_pnls)}, "
            f"window totals={window_trade_count}"
        )

    if abs(trade_net_profit - window_net_profit) > 1e-9:
        raise RuntimeError(
            "OOS trade PnL mismatch: "
            f"trade PnL={trade_net_profit}, "
            f"window PnL={window_net_profit}"
        )

    print()
    print("[2/4] Actual OOS Trade PnL")
    print(f"  OOS trades          : {len(trade_pnls)}")
    print(f"  Total OOS PnL       : {trade_net_profit:,.2f}")

    print()
    print("[3/4] Monte Carlo")

    shuffle_report = run_monte_carlo(
        trade_pnls,
        simulations=5000,
        initial_capital=1_000_000,
        seed=42,
        mode=MonteCarloMode.SHUFFLE,
    )

    bootstrap_report = run_monte_carlo(
        trade_pnls,
        simulations=5000,
        initial_capital=1_000_000,
        seed=42,
        mode=MonteCarloMode.BOOTSTRAP,
    )

    print()
    print("  [SHUFFLE]")
    print(
        f"    Median Final Equity : "
        f"{shuffle_report.median_final_equity:,.2f}"
    )
    print(
        f"    P05 Final Equity    : "
        f"{shuffle_report.p05_final_equity:,.2f}"
    )
    print(
        f"    P95 Final Equity    : "
        f"{shuffle_report.p95_final_equity:,.2f}"
    )
    print(
        f"    Median Max DD       : "
        f"{shuffle_report.median_max_drawdown:,.2f}"
    )
    print(
        f"    Median Max DD %     : "
        f"{shuffle_report.median_max_drawdown_pct:.2%}"
    )

    print()
    print("  [BOOTSTRAP]")
    print(
        f"    Median Final Equity : "
        f"{bootstrap_report.median_final_equity:,.2f}"
    )
    print(
        f"    P05 Final Equity    : "
        f"{bootstrap_report.p05_final_equity:,.2f}"
    )
    print(
        f"    P95 Final Equity    : "
        f"{bootstrap_report.p95_final_equity:,.2f}"
    )
    print(
        f"    Median Max DD       : "
        f"{bootstrap_report.median_max_drawdown:,.2f}"
    )
    print(
        f"    Median Max DD %     : "
        f"{bootstrap_report.median_max_drawdown_pct:.2%}"
    )
    print(
        f"    Probability Loss    : "
        f"{bootstrap_report.probability_loss:.2%}"
    )

    print()
    print("[4/4] Writing report")

    report = build_report(
        shuffle_report=shuffle_report,
        bootstrap_report=bootstrap_report,
        oos_results=oos_results,
        trade_pnls=trade_pnls,
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"Report   : {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
