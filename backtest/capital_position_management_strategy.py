from __future__ import annotations

from abc import ABC, abstractmethod

from backtest.fixed_ratio_capital_position_input import (
    FixedRatioCapitalPositionInput,
)


class CapitalPositionManagementStrategy(ABC):
    @abstractmethod
    def calculate(
        self,
        sizing_input: FixedRatioCapitalPositionInput,
    ) -> int:
        raise NotImplementedError
