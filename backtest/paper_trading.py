from __future__ import annotations

from backtest.broker import Broker
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

    def submit_order(self, order: Order) -> Fill:
        if not self.risk_manager.can_open(
            equity=self.portfolio.equity if self.portfolio else 0.0,
            quantity=order.quantity,
        ):
            raise ValueError("Order rejected by risk manager")

        return self.broker.submit_order(order)

    def open_position(
        self,
        signal: Signal,
        order: Order,
    ) -> Position:
        fill = self.submit_order(order)

        position = self.position_manager.open_position(
            signal=signal,
            fill=fill,
        )

        if self.portfolio is not None:
            self.portfolio.open_position(
                direction=position.direction,
                entry_price=position.entry_price,
                quantity=position.quantity,
                commission=fill.commission,
            )

        return position



    def close_position(
        self,
        order: Order,
    ) -> float:
        fill = self.broker.submit_order(order)

        position = self.position_manager.current_position
        if position is None:
            raise RuntimeError("Cannot close position while flat.")

        if self.portfolio is not None:
            pnl = self.portfolio.close_position(
                exit_price=fill.price,
                commission=fill.commission,
            )
        else:
            pnl = 0.0

        self.position_manager.close_position()

        return pnl
