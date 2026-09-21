from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any


@dataclass(frozen=True)
class MonteCarloAnalysis:
    mode: str
    trade_count: int
    simulations: int
    initial_capital: float
    original_total_pnl: float
    original_return_pct: float
    original_final_equity: float

    median_final_equity: float
    p05_final_equity: float
    p95_final_equity: float

    median_total_pnl: float
    p05_total_pnl: float
    p95_total_pnl: float

    median_max_drawdown: float
    p05_max_drawdown: float
    p95_max_drawdown: float

    median_max_drawdown_pct: float
    p05_max_drawdown_pct: float
    p95_max_drawdown_pct: float

    probability_positive: float
    probability_loss: float

    min_final_equity: float
    max_final_equity: float
    min_total_pnl: float
    max_total_pnl: float
    worst_drawdown: float
    worst_drawdown_pct: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "trade_count": self.trade_count,
            "simulations": self.simulations,
            "initial_capital": self.initial_capital,
            "original_total_pnl": self.original_total_pnl,
            "original_return_pct": self.original_return_pct,
            "original_final_equity": self.original_final_equity,
            "median_final_equity": self.median_final_equity,
            "p05_final_equity": self.p05_final_equity,
            "p95_final_equity": self.p95_final_equity,
            "median_total_pnl": self.median_total_pnl,
            "p05_total_pnl": self.p05_total_pnl,
            "p95_total_pnl": self.p95_total_pnl,
            "median_max_drawdown": self.median_max_drawdown,
            "p05_max_drawdown": self.p05_max_drawdown,
            "p95_max_drawdown": self.p95_max_drawdown,
            "median_max_drawdown_pct": self.median_max_drawdown_pct,
            "p05_max_drawdown_pct": self.p05_max_drawdown_pct,
            "p95_max_drawdown_pct": self.p95_max_drawdown_pct,
            "probability_positive": self.probability_positive,
            "probability_loss": self.probability_loss,
            "min_final_equity": self.min_final_equity,
            "max_final_equity": self.max_final_equity,
            "min_total_pnl": self.min_total_pnl,
            "max_total_pnl": self.max_total_pnl,
            "worst_drawdown": self.worst_drawdown,
            "worst_drawdown_pct": self.worst_drawdown_pct,
        }


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        raise ValueError("values must not be empty")

    ordered = sorted(values)

    if len(ordered) == 1:
        return ordered[0]

    position = (len(ordered) - 1) * percentile
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower

    return ordered[lower] + (ordered[upper] - ordered[lower]) * weight


def analyze_monte_carlo_report(
    report: dict[str, Any],
) -> MonteCarloAnalysis:
    mode = str(report["mode"])
    trade_count = int(report["trade_count"])
    simulations = int(report["simulations"])
    initial_capital = float(report["initial_capital"])
    original_total_pnl = float(report["original_total_pnl"])
    original_final_equity = float(report["original_final_equity"])

    simulations_result = report.get("simulations_result", [])
    if not simulations_result:
        raise ValueError("Monte Carlo report contains no simulation results")

    final_equities = [
        float(item["final_equity"])
        for item in simulations_result
    ]
    total_pnls = [
        float(item["total_pnl"])
        for item in simulations_result
    ]
    max_drawdowns = [
        float(item["max_drawdown"])
        for item in simulations_result
    ]
    max_drawdown_pcts = [
        float(item["max_drawdown_pct"])
        for item in simulations_result
    ]

    return_pct = (
        original_total_pnl / initial_capital * 100.0
        if initial_capital
        else 0.0
    )

    positive_count = sum(value > 0 for value in total_pnls)

    return MonteCarloAnalysis(
        mode=mode,
        trade_count=trade_count,
        simulations=simulations,
        initial_capital=initial_capital,
        original_total_pnl=original_total_pnl,
        original_return_pct=return_pct,
        original_final_equity=original_final_equity,
        median_final_equity=median(final_equities),
        p05_final_equity=_percentile(final_equities, 0.05),
        p95_final_equity=_percentile(final_equities, 0.95),
        median_total_pnl=median(total_pnls),
        p05_total_pnl=_percentile(total_pnls, 0.05),
        p95_total_pnl=_percentile(total_pnls, 0.95),
        median_max_drawdown=median(max_drawdowns),
        p05_max_drawdown=_percentile(max_drawdowns, 0.05),
        p95_max_drawdown=_percentile(max_drawdowns, 0.95),
        median_max_drawdown_pct=median(max_drawdown_pcts),
        p05_max_drawdown_pct=_percentile(max_drawdown_pcts, 0.05),
        p95_max_drawdown_pct=_percentile(max_drawdown_pcts, 0.95),
        probability_positive=positive_count / len(total_pnls),
        probability_loss=1.0 - positive_count / len(total_pnls),
        min_final_equity=min(final_equities),
        max_final_equity=max(final_equities),
        min_total_pnl=min(total_pnls),
        max_total_pnl=max(total_pnls),
        worst_drawdown=min(max_drawdowns),
        worst_drawdown_pct=min(max_drawdown_pcts),
    )


def analyze_monte_carlo_file(path: str | Path) -> MonteCarloAnalysis:
    report_path = Path(path)

    with report_path.open("r", encoding="utf-8") as handle:
        report = json.load(handle)

    return analyze_monte_carlo_report(report)
