from __future__ import annotations

import shioaji as sj

from backtest.models import Order, OrderStatus, OrderType
from trading.account import PositionDirection
from trading.execution import (
    OrderIntent,
    PositionEffect,
    validate_order_intent_consistency,
)


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


def to_shioaji_action(
    direction: PositionDirection,
    effect: PositionEffect,
) -> sj.Action:
    if direction == PositionDirection.LONG and effect == PositionEffect.OPEN:
        return sj.Action.Buy
    if direction == PositionDirection.SHORT and effect == PositionEffect.OPEN:
        return sj.Action.Sell
    if direction == PositionDirection.LONG:
        return sj.Action.Sell
    return sj.Action.Buy


def to_shioaji_octype(effect: PositionEffect) -> sj.FuturesOCType:
    if effect == PositionEffect.OPEN:
        return sj.FuturesOCType.New
    return sj.FuturesOCType.Cover


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
    intent: OrderIntent,
) -> sj.FuturesOrder:
    validate_order_intent_consistency(
        order_direction=order.direction.value,
        order_quantity=order.quantity,
        intent=intent,
    )
    return sj.FuturesOrder(
        action=to_shioaji_action(
            intent.position_direction,
            intent.position_effect,
        ),
        price=order.requested_price or 0.0,
        quantity=order.quantity,
        price_type=to_shioaji_price_type(order.order_type),
        order_type=to_shioaji_order_type(),
        octype=to_shioaji_octype(intent.position_effect),
    )
