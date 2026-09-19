from __future__ import annotations

from dataclasses import dataclass

from backtest.models import Direction


@dataclass(frozen=True)
class CostConfig:
    commission_per_contract: float = 0.0
    slippage_points: float = 0.0


@dataclass(frozen=True)
class ExecutionCost:
    requested_price: float
    fill_price: float
    slippage_points: float
    commission: float


class CostCalculator:
    def __init__(
        self,
        config: CostConfig,
    ):
        self.config = config

    def apply_slippage(
        self,
        price: float,
        direction: Direction,
        is_entry: bool,
    ) -> float:

        slippage = self.config.slippage_points

        if slippage < 0:
            raise ValueError(
                "slippage_points must be >= 0"
            )

        if direction == Direction.LONG:

            if is_entry:
                return price + slippage

            return price - slippage

        if direction == Direction.SHORT:

            if is_entry:
                return price - slippage

            return price + slippage

        raise ValueError(
            f"Unsupported direction: {direction}"
        )

    def commission(
        self,
        quantity: int,
    ) -> float:

        if quantity <= 0:
            raise ValueError(
                "quantity must be > 0"
            )

        return (
            self.config.commission_per_contract
            * quantity
        )

    def calculate_execution_cost(
        self,
        requested_price: float,
        direction: Direction,
        quantity: int,
        is_entry: bool,
    ) -> ExecutionCost:

        fill_price = self.apply_slippage(
            price=requested_price,
            direction=direction,
            is_entry=is_entry,
        )

        slippage_points = abs(
            fill_price - requested_price
        )

        commission = self.commission(
            quantity
        )

        return ExecutionCost(
            requested_price=requested_price,
            fill_price=fill_price,
            slippage_points=slippage_points,
            commission=commission,
        )

    def slippage_cost(
        self,
        entry_requested_price: float,
        entry_fill_price: float,
        exit_requested_price: float,
        exit_fill_price: float,
        quantity: int,
        multiplier: float,
    ) -> float:

        entry_difference = abs(
            entry_fill_price
            - entry_requested_price
        )

        exit_difference = abs(
            exit_fill_price
            - exit_requested_price
        )

        return (
            entry_difference
            + exit_difference
        ) * quantity * multiplier
