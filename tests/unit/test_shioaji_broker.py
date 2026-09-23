from datetime import datetime
from types import SimpleNamespace

import shioaji as sj
import pytest

from backtest.execution_result import OrderSubmission
from backtest.models import Direction, Fill, Order, OrderStatus, OrderType
from backtest.shioaji_broker import ShioajiBroker


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


def make_deal(price: float, quantity: int, ts: float):
    return SimpleNamespace(
        price=price,
        quantity=quantity,
        ts=ts,
        datetime=datetime.fromtimestamp(ts),
    )


def test_get_fills_returns_all_shioaji_deals():
    api = FakeAPI()

    api.trade.status.deals = [
        make_deal(20000, 1, 1767574800),
        make_deal(20005, 2, 1767574860),
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

    result = broker.submit_order(make_order())

    assert isinstance(result, OrderSubmission)
    assert result.order.order_id == "ENTRY-001"
    assert result.order.status == OrderStatus.SUBMITTED
    assert result.fills == []