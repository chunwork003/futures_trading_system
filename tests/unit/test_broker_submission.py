from datetime import datetime

from backtest.broker import Broker
from backtest.execution_result import OrderSubmission
from backtest.models import (
    Direction,
    Fill,
    Order,
    OrderStatus,
    OrderType,
)


class DummyBroker(Broker):
    def submit_order(self, order: Order) -> OrderSubmission:
        return OrderSubmission(
            order=order,
            fills=[],
        )

    def get_order(self, order_id: str) -> Order | None:
        return None

    def get_fills(self, order_id: str) -> list[Fill]:
        return []

    def cancel_order(self, order_id: str) -> Order:
        raise NotImplementedError


def test_broker_submit_order_returns_order_submission():
    broker = DummyBroker()

    order = Order(
        order_id="ORD-001",
        signal_id="SIG-001",
        timestamp=datetime(2026, 1, 5, 9, 0),
        symbol="TXF",
        contract="TXF202601",
        direction=Direction.LONG,
        order_type=OrderType.MARKET,
        quantity=1,
        requested_price=20_000.0,
        status=OrderStatus.SUBMITTED,
    )

    result = broker.submit_order(order)

    assert isinstance(result, OrderSubmission)
    assert result.order.order_id == "ORD-001"
    assert result.fills == []
