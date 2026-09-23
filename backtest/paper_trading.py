from __future__ import annotations

from dataclasses import dataclass

from backtest.broker import Broker
from backtest.execution_result import OrderSubmission
from backtest.models import Fill, Order, OrderStatus, Position, Signal
from backtest.paper_broker import PaperBroker
from backtest.portfolio import Portfolio
from backtest.position import PositionManager
from backtest.risk import PortfolioRiskManager, RiskConfig


@dataclass(frozen=True)
class PendingOrder:
    order: Order
    signal: Signal | None = None


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
        self._pending_orders: dict[str, PendingOrder] = {}

    @property
    def pending_orders(self) -> dict[str, PendingOrder]:
        return dict(self._pending_orders)

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

    def sync_pending_order(self, order_id: str) -> Position | None:
        pending = self._pending_orders.get(order_id)
        if pending is None:
            raise ValueError(f"Pending order not found: {order_id}")

        fills = self.broker.get_fills(order_id)
        current_order = self.broker.get_order(order_id)

        if not fills:
            if current_order is not None and current_order.status in {
                OrderStatus.CANCELLED,
                OrderStatus.REJECTED,
            }:
                del self._pending_orders[order_id]
            return None

        if pending.signal is None:
            pnl = self.apply_exit_fills(
                fills=fills,
            )

            if current_order is not None and current_order.status in {
                OrderStatus.FILLED,
                OrderStatus.CANCELLED,
                OrderStatus.REJECTED,
            }:
                del self._pending_orders[order_id]

            return pnl

        position = self.apply_entry_fills(
            signal=pending.signal,
            fills=fills,
        )

        if current_order is not None and current_order.status in {
            OrderStatus.FILLED,
            OrderStatus.CANCELLED,
            OrderStatus.REJECTED,
        }:
            del self._pending_orders[order_id]

        return position

    def open_position(
        self,
        signal: Signal,
        order: Order,
    ) -> Position | None:
        submission = self.submit_order(order)

        if not submission.fills:
            self._pending_orders[order.order_id] = PendingOrder(
                order=order,
                signal=signal,
            )
            return None

        return self.apply_entry_fills(
            signal=signal,
            fills=submission.fills,
        )

    def close_position(
        self,
        order: Order,
    ) -> float | None:
        submission: OrderSubmission = self.broker.submit_order(order)

        if not submission.fills:
            self._pending_orders[order.order_id] = PendingOrder(
                order=order,
                signal=None,
            )
            return None

        return self.apply_exit_fills(
            fills=submission.fills,
        )
