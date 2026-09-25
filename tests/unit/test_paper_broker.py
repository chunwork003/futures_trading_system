from datetime import datetime

import pytest

from backtest.models import Direction, Order, OrderStatus, OrderType
from backtest.paper_broker import PaperBroker
from trading.account import PositionDirection
from trading.execution import OrderIntent, PositionEffect


def make_order(
    *,
    order_id: str = "ORD-001",
    status: OrderStatus = OrderStatus.PENDING,
    requested_price: float | None = 20_000.0,
) -> Order:
    return Order(
        order_id=order_id,
        signal_id="SIG-001",
        timestamp=datetime(2026, 1, 5, 9, 0),
        symbol="TXF",
        contract="TXF202601",
        direction=Direction.LONG,
        order_type=OrderType.MARKET,
        quantity=1,
        requested_price=requested_price,
        status=status,
    )


def test_paper_broker_fills_pending_order() -> None:
    broker = PaperBroker()

    result = broker.submit_order(make_order())
    fill = result.fills[0]

    assert fill.order_id == "ORD-001"
    assert fill.requested_price == 20_000.0
    assert fill.price == 20_000.0
    assert fill.quantity == 1


def test_paper_broker_accepts_optional_intent_without_changing_fill() -> None:
    broker = PaperBroker()
    intent = OrderIntent(
        intent_id="INT-001",
        correlation_id="CORR-001",
        position_direction=PositionDirection.LONG,
        position_effect=PositionEffect.OPEN,
        quantity=1,
    )

    result = broker.submit_order(make_order(), intent=intent)

    assert result.fills[0].price == 20_000.0
    assert result.order.status == OrderStatus.FILLED


def test_paper_broker_stores_filled_order() -> None:
    broker = PaperBroker()

    broker.submit_order(make_order())

    stored_order = broker.orders["ORD-001"]

    assert stored_order.status == OrderStatus.FILLED
    assert stored_order.fill_price == 20_000.0


def test_paper_broker_get_order_returns_order() -> None:
    broker = PaperBroker()

    broker.submit_order(make_order())

    order = broker.get_order("ORD-001")

    assert order is not None
    assert order.order_id == "ORD-001"
    assert order.status == OrderStatus.FILLED


def test_paper_broker_get_order_returns_none_for_unknown_order() -> None:
    broker = PaperBroker()

    assert broker.get_order("UNKNOWN") is None


def test_paper_broker_rejects_duplicate_order_id() -> None:
    broker = PaperBroker()

    broker.submit_order(make_order())

    with pytest.raises(ValueError, match="Duplicate order_id"):
        broker.submit_order(make_order())


def test_paper_broker_rejects_non_pending_order() -> None:
    broker = PaperBroker()

    with pytest.raises(ValueError, match="Only PENDING orders can be submitted"):
        broker.submit_order(
            make_order(status=OrderStatus.FILLED)
        )


def test_paper_broker_rejects_missing_requested_price() -> None:
    broker = PaperBroker()

    with pytest.raises(
        ValueError,
        match="requires requested_price",
    ):
        broker.submit_order(
            make_order(requested_price=None)
        )


def test_paper_broker_stores_fill() -> None:
    broker = PaperBroker()

    result = broker.submit_order(make_order())

    fills = broker.get_fills("ORD-001")

    assert len(fills) == 1
    assert fills[0] == result.fills[0]


def test_paper_broker_get_fills_returns_empty_for_unknown_order() -> None:
    broker = PaperBroker()

    assert broker.get_fills("UNKNOWN") == []


def test_paper_broker_cancel_pending_order() -> None:
    broker = PaperBroker()

    order = make_order()
    broker.orders[order.order_id] = order

    cancelled = broker.cancel_order("ORD-001")

    assert cancelled.status == OrderStatus.CANCELLED
    assert broker.orders["ORD-001"].status == OrderStatus.CANCELLED


def test_paper_broker_rejects_cancel_unknown_order() -> None:
    broker = PaperBroker()

    with pytest.raises(ValueError, match="Unknown order_id"):
        broker.cancel_order("UNKNOWN")


def test_paper_broker_rejects_cancel_filled_order() -> None:
    broker = PaperBroker()

    broker.submit_order(make_order())

    with pytest.raises(
        ValueError,
        match="Only PENDING orders can be cancelled",
    ):
        broker.cancel_order("ORD-001")
