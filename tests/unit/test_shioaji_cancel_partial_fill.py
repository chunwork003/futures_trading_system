from types import SimpleNamespace

import shioaji as sj

from backtest.models import OrderStatus
from backtest.shioaji_broker import ShioajiBroker
from tests.unit.test_shioaji_broker import FakeAPI, make_intent, make_order


def test_shioaji_cancel_order_preserves_partial_fills() -> None:
    api = FakeAPI(status=sj.OrderStatus.Cancelled)

    order = make_order()

    api.trade.status.deals = [
        SimpleNamespace(
            datetime=order.timestamp,
            ts=order.timestamp.timestamp(),
            price=20005.0,
            quantity=1,
                seq="TEST-DEAL-001",
        )
    ]

    broker = ShioajiBroker(api)

    submission = broker.submit_order(order, intent=make_intent(order))

    cancelled_order = broker.cancel_order("ENTRY-001")
    fills = submission.fills

    assert cancelled_order.status == OrderStatus.CANCELLED
    assert len(fills) == 1
    assert fills[0].quantity == 1
    assert fills[0].price == 20005.0
