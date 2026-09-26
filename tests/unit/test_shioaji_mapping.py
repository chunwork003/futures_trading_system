from datetime import datetime

import shioaji as sj
import pytest

from backtest.models import Direction, Order, OrderStatus, OrderType
from backtest.shioaji_mapping import (
    UnverifiedBrokerOrderStatusError,
    to_order_status,
    to_shioaji_action,
    to_shioaji_octype,
    to_shioaji_order,
    to_shioaji_order_type,
    to_shioaji_price_type,
)
from trading.account import PositionDirection
from trading.execution import (
    OrderIntent,
    PositionEffect,
    PositionEffectValidationError,
)


def make_order(
    direction: Direction = Direction.LONG,
    order_type: OrderType = OrderType.MARKET,
    order_id: str = "ENTRY-001",
    quantity: int = 1,
) -> Order:
    return Order(
        order_id=order_id,
        signal_id="SIG-001",
        timestamp=datetime(2026, 1, 5, 9, 0),
        symbol="TXF",
        contract="TXF202601",
        direction=direction,
        order_type=order_type,
        quantity=quantity,
        requested_price=20000,
        status=OrderStatus.PENDING,
    )


def make_intent(
    *,
    direction: PositionDirection = PositionDirection.LONG,
    effect: PositionEffect = PositionEffect.OPEN,
    quantity: int = 1,
) -> OrderIntent:
    return OrderIntent(
        intent_id="INT-001",
        correlation_id="CORR-001",
        position_direction=direction,
        position_effect=effect,
        quantity=quantity,
    )


def test_order_status_mapping_for_authoritative_statuses() -> None:
    assert to_order_status(sj.OrderStatus.Filled) == OrderStatus.FILLED
    assert to_order_status(sj.OrderStatus.Cancelled) == OrderStatus.CANCELLED
    assert to_order_status(sj.OrderStatus.PartFilled) == OrderStatus.PARTIALLY_FILLED
    assert to_order_status(sj.OrderStatus.PendingSubmit) == OrderStatus.SUBMITTED
    assert to_order_status(sj.OrderStatus.Submitted) == OrderStatus.SUBMITTED


@pytest.mark.parametrize(
    "status",
    [
        sj.OrderStatus.PreSubmitted,
        sj.OrderStatus.Inactive,
        sj.OrderStatus.Failed,
    ],
)
def test_unverified_order_statuses_fail_closed(
    status: sj.OrderStatus,
) -> None:
    with pytest.raises(
        UnverifiedBrokerOrderStatusError
    ) as exc_info:
        to_order_status(status)

    assert exc_info.value.status is status
    assert repr(status) in str(exc_info.value)
    assert "capability-unverified" in str(exc_info.value)


def test_unknown_order_status_fails_closed_without_pending_fallback() -> None:
    unknown_status = object()

    with pytest.raises(
        UnverifiedBrokerOrderStatusError
    ) as exc_info:
        to_order_status(unknown_status)  # type: ignore[arg-type]

    assert exc_info.value.status is unknown_status
    assert repr(unknown_status) in str(exc_info.value)


@pytest.mark.parametrize(
    ("direction", "effect", "action", "octype"),
    [
        (PositionDirection.LONG, PositionEffect.OPEN, sj.Action.Buy, sj.FuturesOCType.New),
        (PositionDirection.SHORT, PositionEffect.OPEN, sj.Action.Sell, sj.FuturesOCType.New),
        (PositionDirection.LONG, PositionEffect.REDUCE, sj.Action.Sell, sj.FuturesOCType.Cover),
        (PositionDirection.SHORT, PositionEffect.REDUCE, sj.Action.Buy, sj.FuturesOCType.Cover),
        (PositionDirection.LONG, PositionEffect.CLOSE, sj.Action.Sell, sj.FuturesOCType.Cover),
        (PositionDirection.SHORT, PositionEffect.CLOSE, sj.Action.Buy, sj.FuturesOCType.Cover),
    ],
)
def test_explicit_position_effect_mapping_matrix(
    direction: PositionDirection,
    effect: PositionEffect,
    action: sj.Action,
    octype: sj.FuturesOCType,
) -> None:
    assert to_shioaji_action(direction, effect) == action
    assert to_shioaji_octype(effect) == octype
    assert octype not in {sj.FuturesOCType.Auto, sj.FuturesOCType.DayTrade}


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
        make_intent(),
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
        make_intent(direction=PositionDirection.SHORT),
    )

    assert result.action == sj.Action.Sell
    assert result.octype == sj.FuturesOCType.New


def test_to_shioaji_limit_order():
    order = make_order(order_type=OrderType.LIMIT)
    result = to_shioaji_order(
        order,
        make_intent(),
    )

    assert result.price_type == sj.FuturesPriceType.LMT


def test_to_shioaji_stop_order():
    order = make_order(order_type=OrderType.STOP)
    result = to_shioaji_order(
        order,
        make_intent(),
    )

    assert result.price_type == sj.FuturesPriceType.MKT


def test_order_id_prefix_has_no_execution_semantics() -> None:
    entry_close = to_shioaji_order(
        make_order(order_id="ENTRY-001"),
        make_intent(effect=PositionEffect.CLOSE),
    )
    exit_open = to_shioaji_order(
        make_order(order_id="EXIT-001"),
        make_intent(effect=PositionEffect.OPEN),
    )

    assert entry_close.action == sj.Action.Sell
    assert entry_close.octype == sj.FuturesOCType.Cover
    assert exit_open.action == sj.Action.Buy
    assert exit_open.octype == sj.FuturesOCType.New


def test_order_intent_quantity_mismatch_is_rejected() -> None:
    with pytest.raises(PositionEffectValidationError, match="quantity"):
        to_shioaji_order(
            make_order(quantity=2),
            make_intent(quantity=1),
        )


def test_order_intent_direction_mismatch_is_rejected() -> None:
    with pytest.raises(PositionEffectValidationError, match="direction"):
        to_shioaji_order(
            make_order(direction=Direction.LONG),
            make_intent(direction=PositionDirection.SHORT),
        )
