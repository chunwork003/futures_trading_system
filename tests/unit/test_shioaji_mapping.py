from datetime import datetime

import shioaji as sj

from backtest.models import Direction, Order, OrderStatus, OrderType
from backtest.shioaji_mapping import (
    to_order_status,
    to_shioaji_action,
    to_shioaji_order,
    to_shioaji_order_type,
    to_shioaji_price_type,
)


def make_order(
    direction: Direction = Direction.LONG,
    order_type: OrderType = OrderType.MARKET,
) -> Order:
    return Order(
        order_id="ENTRY-001",
        signal_id="SIG-001",
        timestamp=datetime(2026, 1, 5, 9, 0),
        symbol="TXF",
        contract="TXF202601",
        direction=direction,
        order_type=order_type,
        quantity=1,
        requested_price=20000,
        status=OrderStatus.PENDING,
    )


def test_order_status_mapping():
    assert to_order_status(sj.OrderStatus.Filled) == OrderStatus.FILLED
    assert to_order_status(sj.OrderStatus.Cancelled) == OrderStatus.CANCELLED
    assert to_order_status(sj.OrderStatus.Inactive) == OrderStatus.REJECTED
    assert to_order_status(sj.OrderStatus.Failed) == OrderStatus.REJECTED
    assert to_order_status(sj.OrderStatus.PartFilled) == OrderStatus.PARTIALLY_FILLED
    assert to_order_status(sj.OrderStatus.PendingSubmit) == OrderStatus.SUBMITTED
    assert to_order_status(sj.OrderStatus.PreSubmitted) == OrderStatus.SUBMITTED
    assert to_order_status(sj.OrderStatus.Submitted) == OrderStatus.SUBMITTED


def test_to_shioaji_action():
    assert to_shioaji_action(Direction.LONG) == sj.Action.Buy
    assert to_shioaji_action(Direction.SHORT) == sj.Action.Sell


def test_to_shioaji_price_type():
    assert to_shioaji_price_type(OrderType.MARKET) == sj.FuturesPriceType.MKP
    assert to_shioaji_price_type(OrderType.LIMIT) == sj.FuturesPriceType.LMT
    assert to_shioaji_price_type(OrderType.STOP) == sj.FuturesPriceType.MKT


def test_to_shioaji_order_type():
    assert to_shioaji_order_type() == sj.OrderType.ROD


def test_to_shioaji_order():
    order = make_order()
    result = to_shioaji_order(
        order,
        sj.FuturesOCType.New,
    )

    assert result.action == sj.Action.Buy
    assert result.price == 20000
    assert result.quantity == 1
    assert result.price_type == sj.FuturesPriceType.MKP
    assert result.order_type == sj.OrderType.ROD
    assert result.octype == sj.FuturesOCType.New


def test_to_shioaji_short_order():
    order = make_order(direction=Direction.SHORT)
    result = to_shioaji_order(
        order,
        sj.FuturesOCType.Cover,
    )

    assert result.action == sj.Action.Sell
    assert result.octype == sj.FuturesOCType.Cover


def test_to_shioaji_limit_order():
    order = make_order(order_type=OrderType.LIMIT)
    result = to_shioaji_order(
        order,
        sj.FuturesOCType.New,
    )

    assert result.price_type == sj.FuturesPriceType.LMT


def test_to_shioaji_stop_order():
    order = make_order(order_type=OrderType.STOP)
    result = to_shioaji_order(
        order,
        sj.FuturesOCType.New,
    )

    assert result.price_type == sj.FuturesPriceType.MKT
