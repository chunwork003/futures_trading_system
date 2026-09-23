from __future__ import annotations

from backtest.broker import Broker
from backtest.execution_result import OrderSubmission
from backtest.models import Fill, Order, Position, Signal
from backtest.paper_broker import PaperBroker
from backtest.portfolio import Portfolio
from backtest.position import PositionManager
from backtest.risk import PortfolioRiskManager, RiskConfig


class PaperTradingEngine:
    def __init__(
        self,
        broker: Broker | None = None,
        position_manager: PositionManager | None = None,
        portfolio: Portfolio | None = None,
        risk_manager: PortfolioRiskManager | None = None,
    ) -> None:
        self.broker = broker or PaperBroker()
        self.position_manager = position_manager or PositionManager()
        self.portfolio = portfolio
        self.risk_manager = risk_manager or PortfolioRiskManager(
            RiskConfig()
        )

    def submit_order(self, order: Order) -> OrderSubmission:
        if not self.risk_manager.can_open(
            equity=self.portfolio.equity if self.portfolio else 0.0,
            quantity=order.quantity,
        ):
            raise ValueError("Order rejected by risk manager")

        return self.broker.submit_order(order)

    def apply_entry_fills(
        self,
        signal: Signal,
        fills: list[Fill],
    ) -> Position:
        if not fills:
            raise RuntimeError(
                f"Order has not been filled: {signal.signal_id}"
            )

        position = self.position_manager.open_position(
            signal=signal,
            fill=fills[0],
        )

        for fill in fills[1:]:
            position = self.position_manager.add_fill(fill=fill)

        if self.portfolio is not None:
            self.portfolio.open_position(
                direction=position.direction,
                entry_price=position.entry_price,
                quantity=position.quantity,
                commission=position.entry_commission,
            )

        return position

    def apply_exit_fills(
        self,
        fills: list[Fill],
    ) -> float:
        if not fills:
            raise RuntimeError("Order has not been filled.")

        position = self.position_manager.current_position
        if position is None:
            raise RuntimeError("Cannot close position while flat.")

        total_pnl = 0.0

        for fill in fills:
            if self.portfolio is not None:
                total_pnl += self.portfolio.close_position(
                    exit_price=fill.price,
                    commission=fill.commission,
                    quantity=fill.quantity,
                )

            self.position_manager.reduce_position(
                quantity=fill.quantity,
            )

        return total_pnl

    def open_position(
        self,
        signal: Signal,
        order: Order,
    ) -> Position:
        submission = self.submit_order(order)

        return self.apply_entry_fills(
            signal=signal,
            fills=submission.fills,
        )

    def close_position(
        self,
        order: Order,
    ) -> float:
        submission: OrderSubmission = self.broker.submit_order(order)

        return self.apply_exit_fills(
            fills=submission.fills,
        )
