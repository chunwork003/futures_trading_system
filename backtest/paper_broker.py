from __future__ import annotations

from backtest.broker import Broker
from backtest.models import Fill, Order, OrderStatus


class PaperBroker(Broker):
    def __init__(self) -> None:
        self.orders: dict[str, Order] = {}

    def submit_order(self, order: Order) -> Fill:
        if order.status != OrderStatus.PENDING:
            raise ValueError("Only PENDING orders can be submitted")

        if order.requested_price is None:
            raise ValueError("PaperBroker requires requested_price")

        if order.order_id in self.orders:
            raise ValueError(f"Duplicate order_id: {order.order_id}")

        filled_order = order.model_copy(
            update={
                "status": OrderStatus.FILLED,
                "fill_price": order.requested_price,
            }
        )
        self.orders[order.order_id] = filled_order

        return Fill(
            order_id=order.order_id,
            timestamp=order.timestamp,
            requested_price=order.requested_price,
            price=order.requested_price,
            quantity=order.quantity,
        )

    def get_order(self, order_id: str) -> Order | None:
        return self.orders.get(order_id)

    def cancel_order(self, order_id: str) -> Order:
        order = self.orders.get(order_id)

        if order is None:
            raise ValueError(f"Unknown order_id: {order_id}")

        if order.status != OrderStatus.PENDING:
            raise ValueError("Only PENDING orders can be cancelled")

        cancelled_order = order.model_copy(
            update={
                "status": OrderStatus.CANCELLED,
            }
        )
        self.orders[order_id] = cancelled_order

        return cancelled_order
