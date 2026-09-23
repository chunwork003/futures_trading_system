from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class PortfolioPosition:
    direction: str
    entry_price: float
    quantity: int


class Portfolio:
    """
    Futures portfolio accounting.

    Responsibilities:
    - Track realized PnL.
    - Track unrealized PnL.
    - Mark position to market.
    - Track equity.
    - Track commissions.

    This class does not calculate commission rates or execution
    slippage. Those responsibilities belong to CostCalculator
    and ExecutionEngine.
    """

    def __init__(
        self,
        initial_capital: float,
        multiplier: float,
    ) -> None:
        if initial_capital < 0:
            raise ValueError("initial_capital must be >= 0")

        if multiplier <= 0:
            raise ValueError("multiplier must be > 0")

        self.initial_capital = float(initial_capital)
        self.multiplier = float(multiplier)

        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0
        self.commission_paid = 0.0

        self.position: Optional[PortfolioPosition] = None

    @property
    def equity(self) -> float:
        return (
            self.initial_capital
            + self.realized_pnl
            + self.unrealized_pnl
        )

    def open_position(
        self,
        direction: str,
        entry_price: float,
        quantity: int,
        commission: float = 0.0,
    ) -> None:
        if self.position is not None:
            raise RuntimeError(
                "Cannot open a new position while portfolio is already invested."
            )

        if direction not in {"LONG", "SHORT"}:
            raise ValueError(
                "direction must be 'LONG' or 'SHORT'"
            )

        if quantity <= 0:
            raise ValueError("quantity must be > 0")

        if commission < 0:
            raise ValueError("commission must be >= 0")

        self.position = PortfolioPosition(
            direction=direction,
            entry_price=float(entry_price),
            quantity=int(quantity),
        )

        self.commission_paid += float(commission)
        self.realized_pnl -= float(commission)

        self.unrealized_pnl = 0.0

    def mark_to_market(self, market_price: float) -> float:
        if self.position is None:
            self.unrealized_pnl = 0.0
            return self.unrealized_pnl

        position = self.position

        if position.direction == "LONG":
            points = market_price - position.entry_price
        else:
            points = position.entry_price - market_price

        self.unrealized_pnl = (
            points
            * position.quantity
            * self.multiplier
        )

        return self.unrealized_pnl

    def close_position(
        self,
        exit_price: float,
        commission: float = 0.0,
        quantity: Optional[int] = None,
    ) -> float:
        if self.position is None:
            raise RuntimeError("Cannot close portfolio while flat.")

        if commission < 0:
            raise ValueError("commission must be >= 0")

        position = self.position

        close_quantity = (
            position.quantity
            if quantity is None
            else quantity
        )

        if close_quantity <= 0:
            raise ValueError("quantity must be > 0")

        if close_quantity > position.quantity:
            raise ValueError(
                "quantity cannot exceed current position quantity"
            )

        if position.direction == "LONG":
            points = exit_price - position.entry_price
        else:
            points = position.entry_price - exit_price

        gross_pnl = (
            points
            * close_quantity
            * self.multiplier
        )

        commission = float(commission)

        net_pnl = gross_pnl - commission

        self.realized_pnl += net_pnl
        self.commission_paid += commission

        remaining_quantity = position.quantity - close_quantity

        if remaining_quantity == 0:
            self.unrealized_pnl = 0.0
            self.position = None
        else:
            position.quantity = remaining_quantity
            self.unrealized_pnl = 0.0

        return net_pnl

    def reset(self) -> None:
        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0
        self.commission_paid = 0.0
        self.position = None
