from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class LocalSensitivityGrid:
    fast_windows: tuple[int, ...]
    slow_windows: tuple[int, ...]

    def generate(self) -> list[tuple[int, int]]:
        parameters: list[tuple[int, int]] = []

        for fast_window in self.fast_windows:
            for slow_window in self.slow_windows:
                if fast_window < slow_window:
                    parameters.append(
                        (fast_window, slow_window)
                    )

        return parameters


DEFAULT_LOCAL_GRID = LocalSensitivityGrid(
    fast_windows=(10, 15, 20),
    slow_windows=(40, 45, 50, 55, 60),
)


def generate_local_parameter_grid(
    grid: LocalSensitivityGrid = DEFAULT_LOCAL_GRID,
) -> list[tuple[int, int]]:
    return grid.generate()
