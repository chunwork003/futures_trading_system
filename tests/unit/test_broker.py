from datetime import datetime

import pytest

from backtest.broker import Broker
from backtest.models import Direction, Fill, Order, OrderStatus, OrderType


class DummyBroker(Broker):
    def submit_order(self, order: Order) -> Fill:
        return Fill(
            order_id=order.order_id,
            timestamp=order.timestamp,
            requested_price=order.requested_price or 0.0,
            price=order.requested_price or 0.0,
            quantity=order.quantity,
        )

    def get_order(self, order_id: str) -> Order | None:
        return None

    def get_fills(self, order_id: str) -> list[Fill]:
        return []

    def cancel_order(self, order_id: str) -> Order:
        raise NotImplementedError


def test_broker_submit_order_returns_fill() -> None:
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
        status=OrderStatus.PENDING,
    )

    fill = broker.submit_order(order)

    assert isinstance(fill, Fill)
    assert fill.order_id == "ORD-001"
    assert fill.price == 20_000.0
    assert fill.quantity == 1


def test_broker_is_abstract() -> None:
    with pytest.raises(TypeError):
        Broker()
