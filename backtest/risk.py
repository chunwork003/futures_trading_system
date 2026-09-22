from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskConfig:
    initial_margin_per_contract: float = 0.0
    maintenance_margin_per_contract: float = 0.0
    max_contracts: int = 1
    max_margin_utilization: float = 1.0

    def __post_init__(self) -> None:
        if self.initial_margin_per_contract < 0:
            raise ValueError(
                "initial_margin_per_contract must be >= 0"
            )

        if self.maintenance_margin_per_contract < 0:
            raise ValueError(
                "maintenance_margin_per_contract must be >= 0"
            )

        if (
            self.maintenance_margin_per_contract
            > self.initial_margin_per_contract
        ):
            raise ValueError(
                "maintenance_margin_per_contract must be <= "
                "initial_margin_per_contract"
            )

        if self.max_contracts <= 0:
            raise ValueError("max_contracts must be > 0")

        if not 0 < self.max_margin_utilization <= 1:
            raise ValueError(
                "max_margin_utilization must be > 0 and <= 1"
            )


@dataclass(frozen=True)
class RiskState:
    equity: float
    quantity: int
    initial_margin: float
    maintenance_margin: float
    available_capital: float
    margin_utilization: float
    position_exposure: float


class PortfolioRiskManager:
    def __init__(self, config: RiskConfig) -> None:
        self.config = config

    def initial_margin_required(self, quantity: int) -> float:
        self._validate_quantity(quantity)
        return (
            quantity
            * self.config.initial_margin_per_contract
        )

    def maintenance_margin_required(self, quantity: int) -> float:
        self._validate_quantity(quantity)
        return (
            quantity
            * self.config.maintenance_margin_per_contract
        )

    def available_capital(
        self,
        equity: float,
        quantity: int = 0,
    ) -> float:
        if equity < 0:
            raise ValueError("equity must be >= 0")

        margin = self.initial_margin_required(quantity)
        return max(0.0, equity - margin)

    def margin_utilization(
        self,
        equity: float,
        quantity: int,
    ) -> float:
        if equity <= 0:
            raise ValueError("equity must be > 0")

        margin = self.initial_margin_required(quantity)

        if margin == 0:
            return 0.0

        return margin / equity

    def position_exposure(
        self,
        price: float,
        quantity: int,
        multiplier: float,
    ) -> float:
        if price < 0:
            raise ValueError("price must be >= 0")

        if multiplier <= 0:
            raise ValueError("multiplier must be > 0")

        self._validate_quantity(quantity)

        return price * quantity * multiplier

    def can_open(
        self,
        equity: float,
        quantity: int,
    ) -> bool:
        if equity < 0:
            raise ValueError("equity must be >= 0")

        self._validate_quantity(quantity)

        if quantity > self.config.max_contracts:
            return False

        required = self.initial_margin_required(quantity)

        if required == 0:
            return True

        if equity <= 0:
            return False

        return (
            required / equity
            <= self.config.max_margin_utilization
        )

    def should_force_liquidate(
        self,
        equity: float,
        quantity: int,
    ) -> bool:
        if equity < 0:
            raise ValueError("equity must be >= 0")

        self._validate_quantity(quantity)

        if quantity == 0:
            return False

        required = self.maintenance_margin_required(quantity)

        if required == 0:
            return False

        return equity < required

    def snapshot(
        self,
        equity: float,
        quantity: int,
        price: float,
        multiplier: float,
    ) -> RiskState:
        if equity < 0:
            raise ValueError("equity must be >= 0")

        self._validate_quantity(quantity)

        initial_margin = self.initial_margin_required(quantity)
        maintenance_margin = (
            self.maintenance_margin_required(quantity)
        )

        utilization = (
            0.0
            if equity == 0
            else initial_margin / equity
        )

        return RiskState(
            equity=equity,
            quantity=quantity,
            initial_margin=initial_margin,
            maintenance_margin=maintenance_margin,
            available_capital=max(
                0.0,
                equity - initial_margin,
            ),
            margin_utilization=utilization,
            position_exposure=self.position_exposure(
                price=price,
                quantity=quantity,
                multiplier=multiplier,
            ),
        )

    def _validate_quantity(self, quantity: int) -> None:
        if quantity < 0:
            raise ValueError("quantity must be >= 0")
