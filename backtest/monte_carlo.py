from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
from statistics import median
from typing import Sequence


class MonteCarloMode(str, Enum):
    SHUFFLE = "SHUFFLE"
    BOOTSTRAP = "BOOTSTRAP"


@dataclass(frozen=True)
class MonteCarloConfig:
    simulations: int = 5000
    initial_capital: float = 1_000_000.0
    seed: int = 42

    def __post_init__(self) -> None:
        if self.simulations <= 0:
            raise ValueError("simulations must be greater than 0")

        if self.initial_capital <= 0:
            raise ValueError("initial_capital must be greater than 0")


@dataclass(frozen=True)
class MonteCarloSimulationResult:
    final_equity: float
    total_pnl: float
    max_drawdown: float
    max_drawdown_pct: float


@dataclass(frozen=True)
class MonteCarloReport:
    mode: MonteCarloMode
    trade_count: int
    simulations: int
    initial_capital: float

    original_total_pnl: float
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

    simulations_result: tuple[MonteCarloSimulationResult, ...]

    def to_dict(self) -> dict:
        return {
            "mode": self.mode.value,
            "trade_count": self.trade_count,
            "simulations": self.simulations,
            "initial_capital": self.initial_capital,
            "original_total_pnl": self.original_total_pnl,
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
            "simulations_result": [
                {
                    "final_equity": item.final_equity,
                    "total_pnl": item.total_pnl,
                    "max_drawdown": item.max_drawdown,
                    "max_drawdown_pct": item.max_drawdown_pct,
                }
                for item in self.simulations_result
            ],
        }


class MonteCarloEngine:
    def __init__(self, config: MonteCarloConfig) -> None:
        self.config = config

    def run(
        self,
        trade_pnls: Sequence[float],
        mode: MonteCarloMode = MonteCarloMode.SHUFFLE,
    ) -> MonteCarloReport:
        if not trade_pnls:
            raise ValueError("trade_pnls must not be empty")

        pnls = [float(value) for value in trade_pnls]
        original_total_pnl = sum(pnls)

        rng = random.Random(self.config.seed)

        results: list[MonteCarloSimulationResult] = []

        for _ in range(self.config.simulations):
            sampled = self._sample(pnls, mode, rng)
            results.append(self._simulate(sampled))

        final_equities = [item.final_equity for item in results]
        total_pnls = [item.total_pnl for item in results]
        max_drawdowns = [item.max_drawdown for item in results]
        max_drawdown_pcts = [
            item.max_drawdown_pct for item in results
        ]

        positive_count = sum(
            1 for item in results if item.total_pnl > 0
        )

        return MonteCarloReport(
            mode=mode,
            trade_count=len(pnls),
            simulations=self.config.simulations,
            initial_capital=self.config.initial_capital,
            original_total_pnl=original_total_pnl,
            original_final_equity=(
                self.config.initial_capital + original_total_pnl
            ),
            median_final_equity=median(final_equities),
            p05_final_equity=self._percentile(final_equities, 0.05),
            p95_final_equity=self._percentile(final_equities, 0.95),
            median_total_pnl=median(total_pnls),
            p05_total_pnl=self._percentile(total_pnls, 0.05),
            p95_total_pnl=self._percentile(total_pnls, 0.95),
            median_max_drawdown=median(max_drawdowns),
            p05_max_drawdown=self._percentile(max_drawdowns, 0.05),
            p95_max_drawdown=self._percentile(max_drawdowns, 0.95),
            median_max_drawdown_pct=median(max_drawdown_pcts),
            p05_max_drawdown_pct=self._percentile(
                max_drawdown_pcts,
                0.05,
            ),
            p95_max_drawdown_pct=self._percentile(
                max_drawdown_pcts,
                0.95,
            ),
            probability_positive=(
                positive_count / len(results)
            ),
            probability_loss=(
                1.0 - positive_count / len(results)
            ),
            simulations_result=tuple(results),
        )

    @staticmethod
    def _sample(
        pnls: list[float],
        mode: MonteCarloMode,
        rng: random.Random,
    ) -> list[float]:
        if mode == MonteCarloMode.SHUFFLE:
            sampled = pnls.copy()
            rng.shuffle(sampled)
            return sampled

        if mode == MonteCarloMode.BOOTSTRAP:
            return [
                rng.choice(pnls)
                for _ in range(len(pnls))
            ]

        raise ValueError(f"unsupported Monte Carlo mode: {mode}")

    def _simulate(
        self,
        pnls: Sequence[float],
    ) -> MonteCarloSimulationResult:
        equity = self.config.initial_capital
        peak = equity
        max_drawdown = 0.0

        for pnl in pnls:
            equity += pnl

            if equity > peak:
                peak = equity

            drawdown = equity - peak

            if drawdown < max_drawdown:
                max_drawdown = drawdown

        max_drawdown_pct = (
            max_drawdown / peak
            if peak > 0
            else 0.0
        )

        return MonteCarloSimulationResult(
            final_equity=equity,
            total_pnl=equity - self.config.initial_capital,
            max_drawdown=max_drawdown,
            max_drawdown_pct=max_drawdown_pct,
        )

    @staticmethod
    def _percentile(
        values: Sequence[float],
        percentile: float,
    ) -> float:
        if not values:
            raise ValueError("values must not be empty")

        if not 0.0 <= percentile <= 1.0:
            raise ValueError(
                "percentile must be between 0 and 1"
            )

        ordered = sorted(values)

        if len(ordered) == 1:
            return ordered[0]

        position = percentile * (len(ordered) - 1)
        lower = int(position)
        upper = min(lower + 1, len(ordered) - 1)
        weight = position - lower

        return (
            ordered[lower]
            + (ordered[upper] - ordered[lower]) * weight
        )


def run_monte_carlo(
    trade_pnls: Sequence[float],
    *,
    simulations: int = 5000,
    initial_capital: float = 1_000_000.0,
    seed: int = 42,
    mode: MonteCarloMode = MonteCarloMode.SHUFFLE,
) -> MonteCarloReport:
    config = MonteCarloConfig(
        simulations=simulations,
        initial_capital=initial_capital,
        seed=seed,
    )

    return MonteCarloEngine(config).run(
        trade_pnls,
        mode=mode,
    )
