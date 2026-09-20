from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtest.optimization import OptimizationResult
from backtest.parameter_stability import (
    ParameterStabilityAnalyzer,
    StabilityConfig,
)


INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "backtest_results"
    / "trend_state_parameter_optimization.json"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "backtest_results"
    / "trend_state_parameter_stability.json"
)


def load_results() -> tuple[list[OptimizationResult], dict]:
    payload = json.loads(INPUT_PATH.read_text(encoding="utf-8"))

    if isinstance(payload, list):
        raw_results = payload
        metadata = {}
    elif isinstance(payload, dict):
        raw_results = payload.get("results")

        if raw_results is None:
            raise ValueError(
                "optimization report does not contain 'results'"
            )

        metadata = {
            key: value
            for key, value in payload.items()
            if key != "results"
        }
    else:
        raise ValueError("invalid optimization report format")

    results = [
        OptimizationResult(**item)
        for item in raw_results
    ]

    return results, metadata


def main() -> None:
    print("=== P6-3 Parameter Stability Analysis ===")
    print(f"Input  : {INPUT_PATH}")

    results, metadata = load_results()

    print(f"Results: {len(results)}")
    print()

    analyzer = ParameterStabilityAnalyzer(
        results,
        StabilityConfig(neighbor_count=3),
    )

    stability_results = analyzer.analyze()

    stability_results.sort(
        key=lambda item: (
            item.expectancy,
            item.profit_factor,
        ),
        reverse=True,
    )

    print("[Parameter Stability]")

    for index, result in enumerate(stability_results, start=1):
        print(
            f"{index:2d}. "
            f"{result.parameter_id:12s} "
            f"Exp={result.expectancy:8.2f} "
            f"NeighborExp={result.neighbor_expectancy_median:8.2f} "
            f"ExpRange={result.expectancy_range:7.2f} "
            f"PF={result.profit_factor:7.4f} "
            f"NeighborPF={result.neighbor_profit_factor_median:7.4f} "
            f"DD={result.max_drawdown_pct:8.2%}"
        )
        print(
            f"    neighbors="
            f"{', '.join(result.neighbor_parameter_ids)}"
        )

    output = {
        **metadata,
        "neighbor_count": 3,
        "results": [
            result.to_dict()
            for result in stability_results
        ],
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
    print(f"Report : {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
