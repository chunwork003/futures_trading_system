from datetime import datetime
from types import SimpleNamespace

import shioaji as sj
import pytest

from backtest.execution_result import OrderSubmission
from backtest.models import Direction, Fill, Order, OrderStatus, OrderType
from backtest.shioaji_broker import ShioajiBroker
from trading.account import PositionDirection
from trading.execution import (
    OrderIntent,
    PositionEffect,
    PositionEffectValidationError,
)


class FakeAPI:
    def __init__(self, status=sj.OrderStatus.Filled):
        self.Contracts = {
            "TXF202601": SimpleNamespace(
                code="TXF202601",
                symbol="TXF202601",
            )
        }
        self.trade = SimpleNamespace(
            contract=self.Contracts["TXF202601"],
            order=SimpleNamespace(
                id="SHIOAJI-001",
            ),
            status=SimpleNamespace(
                status=status,
                deals=[],
            ),
        )

    def place_order(self, contract, order):
        return self.trade

    def update_status(
        self,
        account=None,
        *,
        trade=None,
        timeout=30000,
        cb=None,
    ):
        return None

    def cancel_order(self, trade, timeout=30000, cb=None):
        return None


def make_order() -> Order:
    return Order(
        order_id="ENTRY-001",
        signal_id="SIG-001",
        timestamp=datetime(2026, 1, 5, 9, 0),
        symbol="TXF",
        contract="TXF202601",
        direction=Direction.LONG,
        order_type=OrderType.MARKET,
        quantity=3,
        requested_price=20000,
        status=OrderStatus.PENDING,
    )


def make_intent(
    order: Order | None = None,
    *,
    effect: PositionEffect = PositionEffect.OPEN,
) -> OrderIntent:
    order = order or make_order()
    return OrderIntent(
        intent_id=f"INT-{order.order_id}",
        correlation_id="CORR-001",
        position_direction=PositionDirection(order.direction.value),
        position_effect=effect,
        quantity=order.quantity,
    )


def make_deal(
    price: float,
    quantity: int,
    ts: float,
    seq: str | None = None,
):
    return SimpleNamespace(
        price=price,
        quantity=quantity,
        ts=ts,
        datetime=datetime.fromtimestamp(ts),
        seq=seq or f"DEAL-{int(ts)}",
    )


def test_get_fills_returns_all_shioaji_deals():
    api = FakeAPI()

    api.trade.status.deals = [
        make_deal(20000, 1, 1767574800, "DEAL-001"),
        make_deal(20005, 2, 1767574860, "DEAL-002"),
    ]

    broker = ShioajiBroker(api)
    order = make_order()

    broker._orders[order.order_id] = order
    broker._trades[order.order_id] = api.trade

    fills = broker.get_fills(order.order_id)

    assert len(fills) == 2
    assert all(isinstance(fill, Fill) for fill in fills)
    assert fills[0].quantity == 1
    assert fills[0].price == 20000
    assert fills[1].quantity == 2
    assert fills[1].price == 20005


def test_get_fills_returns_empty_for_unknown_order():
    broker = ShioajiBroker(FakeAPI())

    assert broker.get_fills("UNKNOWN") == []


def test_submit_order_keeps_submitted_order_without_fill():
    api = FakeAPI(status=sj.OrderStatus.Submitted)
    broker = ShioajiBroker(api)

    order = make_order()
    result = broker.submit_order(order, intent=make_intent(order))

    assert isinstance(result, OrderSubmission)
    assert result.order.order_id == "ENTRY-001"
    assert result.order.status == OrderStatus.SUBMITTED
    assert result.fills == []
def test_get_fills_returns_only_new_shioaji_deals() -> None:
    api = FakeAPI()

    api.trade.status.deals = [
        make_deal(20000, 1, 1767574800, "DEAL-001"),
        make_deal(20005, 2, 1767574860, "DEAL-002"),
    ]

    broker = ShioajiBroker(api)
    order = make_order()

    broker._orders[order.order_id] = order
    broker._trades[order.order_id] = api.trade

    first_fills = broker.get_fills(order.order_id)

    assert len(first_fills) == 2
    assert sum(fill.quantity for fill in first_fills) == 3

    api.trade.status.deals = [
        make_deal(20000, 1, 1767574800, "DEAL-001"),
        make_deal(20005, 2, 1767574860, "DEAL-002"),
        make_deal(20010, 5, 1767574920, "DEAL-003"),
    ]

    second_fills = broker.get_fills(order.order_id)

    assert len(second_fills) == 1
    assert second_fills[0].quantity == 5
    assert second_fills[0].price == 20010


def test_submit_order_marks_immediate_fills_as_delivered() -> None:
    api = FakeAPI(status=sj.OrderStatus.Filled)
    api.trade.status.deals = [
        make_deal(20000, 1, 1767574800, "DEAL-001"),
        make_deal(20005, 2, 1767574860, "DEAL-002"),
    ]

    broker = ShioajiBroker(api)
    order = make_order()

    submission = broker.submit_order(order, intent=make_intent(order))

    assert len(submission.fills) == 2

    later_fills = broker.get_fills(order.order_id)

    assert later_fills == []


def test_submit_order_requires_explicit_intent() -> None:
    with pytest.raises(PositionEffectValidationError, match="requires explicit"):
        ShioajiBroker(FakeAPI()).submit_order(make_order())
