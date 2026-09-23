from datetime import datetime

from backtest.execution_result import OrderSubmission
from backtest.models import (
    Direction,
    Fill,
    Order,
    OrderStatus,
    OrderType,
)


def make_order(status: OrderStatus) -> Order:
    return Order(
        order_id="ORD-001",
        signal_id="SIG-001",
        timestamp=datetime(2026, 1, 5, 9, 0),
        symbol="TXF",
        contract="TXF202601",
        direction=Direction.LONG,
        order_type=OrderType.MARKET,
        quantity=3,
        requested_price=20_000.0,
        status=status,
    )


def make_fill(quantity: int, price: float) -> Fill:
    return Fill(
        order_id="ORD-001",
        timestamp=datetime(2026, 1, 5, 9, 0),
        requested_price=20_000.0,
        price=price,
        quantity=quantity,
    )


def test_order_submission_without_fill():
    result = OrderSubmission(
        order=make_order(OrderStatus.SUBMITTED),
        fills=[],
    )

    assert result.order.status == OrderStatus.SUBMITTED
    assert result.fills == []


def test_order_submission_with_full_fill():
    result = OrderSubmission(
        order=make_order(OrderStatus.FILLED),
        fills=[
            make_fill(3, 20_005.0),
        ],
    )

    assert result.order.status == OrderStatus.FILLED
    assert len(result.fills) == 1
    assert result.fills[0].quantity == 3
    assert result.fills[0].price == 20_005.0


def test_order_submission_with_partial_fills():
    result = OrderSubmission(
        order=make_order(OrderStatus.PARTIALLY_FILLED),
        fills=[
            make_fill(1, 20_000.0),
            make_fill(1, 20_005.0),
        ],
    )

    assert result.order.status == OrderStatus.PARTIALLY_FILLED
    assert len(result.fills) == 2
    assert sum(fill.quantity for fill in result.fills) == 2
