from __future__ import annotations

from backtest.broker import Broker
from backtest.execution_result import OrderSubmission
from backtest.models import Fill, Order, OrderStatus


class PaperBroker(Broker):
    def __init__(self) -> None:
        self.orders: dict[str, Order] = {}
        self._fills: dict[str, list[Fill]] = {}

    def submit_order(self, order: Order) -> OrderSubmission:
        if order.status != OrderStatus.PENDING:
            raise ValueError("Only PENDING orders can be submitted")

        if order.requested_price is None:
            raise ValueError("PaperBroker requires requested_price.")

        if order.order_id in self.orders:
            raise ValueError(f"Duplicate order_id: {order.order_id}")

        fill = Fill(
            order_id=order.order_id,
            timestamp=order.timestamp,
            requested_price=order.requested_price,
            price=order.requested_price,
            quantity=order.quantity,
            commission=order.commission,
            slippage_points=order.slippage_points,
        )

        filled_order = order.model_copy(
            update={
                "status": OrderStatus.FILLED,
                "fill_price": fill.price,
            }
        )

        self.orders[order.order_id] = filled_order
        self._fills[order.order_id] = [fill]

        return OrderSubmission(
            order=filled_order,
            fills=[fill],
        )

    def get_order(self, order_id: str) -> Order | None:
        return self.orders.get(order_id)

    def get_fills(self, order_id: str) -> list[Fill]:
        return list(self._fills.get(order_id, []))

    def cancel_order(self, order_id: str) -> Order:
        order = self.orders.get(order_id)

        if order is None:
            raise ValueError(f"Unknown order_id: {order_id}")

        if order.status != OrderStatus.PENDING:
            raise ValueError("Only PENDING orders can be cancelled")

        cancelled_order = order.model_copy(
            update={"status": OrderStatus.CANCELLED}
        )

        self.orders[order_id] = cancelled_order

        return cancelled_order
