from __future__ import annotations

from collections.abc import Callable
from time import sleep
from typing import Any

from backtest.polling import PollingConfig
from backtest.polling_result import PollingResult


class PollingLoop:
    def __init__(
        self,
        callback: Callable[[], Any],
        config: PollingConfig | None = None,
    ) -> None:
        self.callback = callback
        self.config = config or PollingConfig()

    def run(self, max_iterations: int | None = None) -> PollingResult:
        if max_iterations is not None and max_iterations <= 0:
            raise ValueError("max_iterations must be greater than 0")

        iterations = 0
        results: list[Any] = []

        while max_iterations is None or iterations < max_iterations:
            results.append(self.callback())
            iterations += 1

            if max_iterations is None or iterations < max_iterations:
                sleep(self.config.interval_seconds)

        return PollingResult(
            iterations=iterations,
            results=results,
        )
