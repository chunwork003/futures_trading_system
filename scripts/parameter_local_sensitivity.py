from __future__ import annotations

import json
import sys
from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analysis.performance_report import PerformanceReport
from backtest.engine import BacktestConfig, BacktestEngine
from backtest.optimization import TrendParameterSet
from backtest.parameter_sensitivity import generate_local_parameter_grid
from features.trend import trend_features
from strategies.trend_state_exit import TrendStateExitStrategy


DATABASE_PATH = PROJECT_ROOT / "database" / "market.duckdb"

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "backtest_results"
    / "trend_state_local_sensitivity.json"
)

SYMBOL = "TXF"
TIMEFRAME = "1m"
INITIAL_CAPITAL = 1_000_000.0
QUANTITY = 1
MULTIPLIER = 200.0


def load_txf_1m() -> "pl.DataFrame":
    import polars as pl

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

    with duckdb.connect(str(DATABASE_PATH), read_only=True) as conn:
        arrow_table = conn.execute(
            query,
            [SYMBOL],
        ).to_arrow_table()

    return pl.from_arrow(arrow_table)


def run_parameter(
    bars,
    params: TrendParameterSet,
) -> dict:
    featured = trend_features(
        bars,
        fast_window=params.fast_window,
        slow_window=params.slow_window,
    )

    strategy = TrendStateExitStrategy(symbol=SYMBOL)
    strategy.reset()

    signals = []

    for row in featured.iter_rows(named=True):
        signals.extend(strategy.on_bar(row))

    config = BacktestConfig(
        initial_capital=INITIAL_CAPITAL,
        symbol=SYMBOL,
        timeframe=TIMEFRAME,
        quantity=QUANTITY,
        multiplier=MULTIPLIER,
    )

    engine = BacktestEngine(config)

    trades = engine.run(
        bars=featured.iter_rows(named=True),
        signals=signals,
    )

    report = PerformanceReport.from_trades(
        trades,
        equity_curve=engine.equity_curve,
    )

    stats = report.trade_statistics
    metrics = report.performance_metrics

    return {
        "parameter_id": params.parameter_id,
        "fast_window": params.fast_window,
        "slow_window": params.slow_window,
        "total_trades": stats.total_trades,
        "win_rate": stats.win_rate,
        "net_profit": stats.net_profit,
        "average_trade": stats.average_trade,
        "profit_factor": metrics.profit_factor,
        "expectancy": metrics.expectancy,
        "max_drawdown": report.max_drawdown,
        "max_drawdown_pct": report.max_drawdown_pct,
        "final_equity": report.final_equity,
        "is_baseline": (
            params == TrendParameterSet(20, 60)
        ),
    }


def main() -> None:
    print("=== P6-3B Local Parameter Sensitivity ===")
    print(f"Database : {DATABASE_PATH}")
    print(f"Symbol   : {SYMBOL}")
    print()

    bars = load_txf_1m()

    print(
        f"Rows     : {bars.height}"
    )

    parameters = [
        TrendParameterSet(
            fast_window=fast_window,
            slow_window=slow_window,
        )
        for fast_window, slow_window
        in generate_local_parameter_grid()
    ]

    print(
        f"Parameters: {len(parameters)}"
    )
    print()

    results = []

    for index, params in enumerate(parameters, start=1):
        print(
            f"[{index:02d}/{len(parameters):02d}] "
            f"{params.parameter_id}"
        )

        result = run_parameter(
            bars,
            params,
        )

        results.append(result)

    results.sort(
        key=lambda item: (
            item["expectancy"],
            item["profit_factor"],
        ),
        reverse=True,
    )

    print()
    print("[Local Sensitivity Results]")

    for index, result in enumerate(results, start=1):
        baseline = " BASELINE" if result["is_baseline"] else ""

        print(
            f"{index:2d}. "
            f"{result['parameter_id']:12s} "
            f"Exp={result['expectancy']:8.2f} "
            f"PF={result['profit_factor']:7.4f} "
            f"DD={result['max_drawdown_pct']:8.2%} "
            f"Trades={result['total_trades']:6d}"
            f"{baseline}"
        )

    output = {
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME,
        "rows": bars.height,
        "parameter_count": len(results),
        "grid": {
            "fast_windows": [10, 15, 20],
            "slow_windows": [40, 45, 50, 55, 60],
        },
        "results": results,
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            output,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print(f"Report   : {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
