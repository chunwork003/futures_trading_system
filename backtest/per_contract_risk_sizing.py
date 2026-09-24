from __future__ import annotations

from math import floor

from backtest.position_sizing import PositionSizingInput, PositionSizingStrategy


class PerContractRiskSizing(PositionSizingStrategy):
    def __init__(self, risk_per_contract: float) -> None:
        if risk_per_contract <= 0:
            raise ValueError("risk_per_contract must be greater than zero")

        self.risk_per_contract = risk_per_contract

    def calculate(self, sizing_input: PositionSizingInput) -> int:
        risk_amount = sizing_input.equity * sizing_input.risk_budget

        return floor(
            risk_amount / self.risk_per_contract
        )
