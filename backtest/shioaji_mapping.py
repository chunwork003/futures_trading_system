from __future__ import annotations

import shioaji as sj

from backtest.models import Direction, Order, OrderStatus, OrderType


def to_order_status(status: sj.OrderStatus) -> OrderStatus:
    if status == sj.OrderStatus.Filled:
        return OrderStatus.FILLED

    if status == sj.OrderStatus.PartFilled:
        return OrderStatus.PARTIALLY_FILLED

    if status == sj.OrderStatus.Cancelled:
        return OrderStatus.CANCELLED

    if status in {
        sj.OrderStatus.Inactive,
        sj.OrderStatus.Failed,
    }:
        return OrderStatus.REJECTED

    if status in {
        sj.OrderStatus.PendingSubmit,
        sj.OrderStatus.PreSubmitted,
        sj.OrderStatus.Submitted,
    }:
        return OrderStatus.SUBMITTED

    return OrderStatus.PENDING


def to_shioaji_action(direction: Direction) -> sj.Action:
    if direction == Direction.LONG:
        return sj.Action.Buy

    if direction == Direction.SHORT:
        return sj.Action.Sell

    raise ValueError(f"Unsupported direction: {direction}")


def to_shioaji_price_type(
    order_type: OrderType,
) -> sj.FuturesPriceType:
    if order_type == OrderType.MARKET:
        return sj.FuturesPriceType.MKP

    if order_type == OrderType.LIMIT:
        return sj.FuturesPriceType.LMT

    if order_type == OrderType.STOP:
        return sj.FuturesPriceType.MKT

    raise ValueError(f"Unsupported order type: {order_type}")


def to_shioaji_order_type() -> sj.OrderType:
    return sj.OrderType.ROD


def to_shioaji_order(
    order: Order,
    octype: sj.FuturesOCType,
) -> sj.FuturesOrder:
    return sj.FuturesOrder(
        action=to_shioaji_action(order.direction),
        price=order.requested_price or 0.0,
        quantity=order.quantity,
        price_type=to_shioaji_price_type(order.order_type),
        order_type=to_shioaji_order_type(),
        octype=octype,
    )
