from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from strategy.registry import StrategyRegistry


@dataclass(frozen=True)
class StrategyRunResult:
    strategy_id: str
    version: str
    signals: list[Any]


class MultiStrategyRunner:
    def __init__(self, registry: StrategyRegistry) -> None:
        self.registry = registry

    def run(
        self,
        strategy_ids: Iterable[str],
        bars: Any,
        **kwargs: Any,
    ) -> list[StrategyRunResult]:
        results: list[StrategyRunResult] = []

        for strategy_id in strategy_ids:
            definition = self.registry.get(strategy_id)
            strategy = definition.factory(**kwargs)

            if not hasattr(strategy, "generate_signals"):
                raise TypeError(
                    f"strategy {strategy_id} must provide "
                    "generate_signals()"
                )

            signals = list(strategy.generate_signals(bars))

            results.append(
                StrategyRunResult(
                    strategy_id=definition.strategy_id,
                    version=definition.version,
                    signals=signals,
                )
            )

        return results

    def run_combined(
        self,
        strategy_ids: Iterable[str],
        bars: Any,
        **kwargs: Any,
    ) -> list[Any]:
        results = self.run(
            strategy_ids=strategy_ids,
            bars=bars,
            **kwargs,
        )

        combined: list[Any] = []

        for result in results:
            combined.extend(result.signals)

        combined.sort(
            key=lambda signal: (
                signal.timestamp,
                str(signal.strategy_id),
                str(signal.signal_id),
            )
        )

        return combined
