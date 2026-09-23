from __future__ import annotations

from backtest.risk import PortfolioRiskManager
from backtest.target_position import TargetAccountPosition


class GlobalRiskConstraint:
    def __init__(
        self,
        risk_manager: PortfolioRiskManager,
    ) -> None:
        self.risk_manager = risk_manager

    def allows(
        self,
        equity: float,
        target: TargetAccountPosition | None,
    ) -> bool:
        if target is None:
            return True

        return self.risk_manager.can_open(
            equity=equity,
            quantity=target.quantity,
        )
