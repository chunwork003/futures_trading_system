from __future__ import annotations

import json
from pathlib import Path

from analysis.monte_carlo_report import (
    MonteCarloAnalysis,
    analyze_monte_carlo_report,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "backtest_results"
    / "monte_carlo_oos_txf_1m.json"
)
OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "backtest_results"
    / "monte_carlo_oos_txf_1m_analysis.json"
)


def _print_analysis(label: str, result: MonteCarloAnalysis) -> None:
    print(f"\n[{label}]")
    print(f"Mode                  : {result.mode}")
    print(f"Trade count           : {result.trade_count:,}")
    print(f"Simulations           : {result.simulations:,}")
    print(f"Original PnL          : {result.original_total_pnl:,.2f}")
    print(f"Original return       : {result.original_return_pct:.4f}%")
    print(f"Original final equity : {result.original_final_equity:,.2f}")
    print(f"Median final equity   : {result.median_final_equity:,.2f}")
    print(f"P05 final equity      : {result.p05_final_equity:,.2f}")
    print(f"P95 final equity      : {result.p95_final_equity:,.2f}")
    print(f"Median total PnL      : {result.median_total_pnl:,.2f}")
    print(f"P05 total PnL         : {result.p05_total_pnl:,.2f}")
    print(f"P95 total PnL         : {result.p95_total_pnl:,.2f}")
    print(f"Median max DD         : {result.median_max_drawdown:,.2f}")
    print(f"P05 max DD            : {result.p05_max_drawdown:,.2f}")
    print(f"Worst max DD          : {result.worst_drawdown:,.2f}")
    print(
        f"Median max DD %       : "
        f"{result.median_max_drawdown_pct * 100:.2f}%"
    )
    print(
        f"P05 max DD %          : "
        f"{result.p05_max_drawdown_pct * 100:.2f}%"
    )
    print(
        f"Worst max DD %        : "
        f"{result.worst_drawdown_pct * 100:.2f}%"
    )
    print(f"Probability positive  : {result.probability_positive:.2%}")
    print(f"Probability loss      : {result.probability_loss:.2%}")


def _load_reports(path: Path) -> dict[str, dict]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if "shuffle" in payload and "bootstrap" in payload:
        return {
            "shuffle": payload["shuffle"],
            "bootstrap": payload["bootstrap"],
        }

    if "mode" in payload:
        mode = str(payload["mode"]).lower()
        return {mode: payload}

    raise ValueError(
        "Unsupported Monte Carlo report structure. "
        "Expected 'shuffle'/'bootstrap' reports or a single report."
    )


def main() -> None:
    print("=== P9-5 TXF Monte Carlo Result Analysis ===")
    print(f"Input  : {INPUT_PATH}")
    print(f"Output : {OUTPUT_PATH}")

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Monte Carlo report not found: {INPUT_PATH}"
        )

    reports = _load_reports(INPUT_PATH)

    analyses: dict[str, MonteCarloAnalysis] = {}

    for mode, report in reports.items():
        result = analyze_monte_carlo_report(report)
        analyses[mode] = result
        _print_analysis(mode.upper(), result)

    bootstrap = analyses.get("bootstrap")
    if bootstrap is None:
        raise ValueError("Bootstrap Monte Carlo report is required")

    results = {
        "symbol": "TXF",
        "timeframe": "1m",
        "source_report": str(INPUT_PATH),
        "analysis": {
            mode: result.to_dict()
            for mode, result in analyses.items()
        },
        "interpretation": {
            "original_oos_pnl_negative": (
                bootstrap.original_total_pnl < 0
            ),
            "bootstrap_median_pnl_below_zero": (
                bootstrap.median_total_pnl < 0
            ),
            "bootstrap_loss_probability_above_50pct": (
                bootstrap.probability_loss > 0.50
            ),
            "drawdown_over_100pct_present": (
                any(
                    result.worst_drawdown_pct <= -1.0
                    for result in analyses.values()
                )
            ),
        },
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(
            results,
            handle,
            ensure_ascii=False,
            indent=2,
        )

    print(f"\nAnalysis written: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
