from types import SimpleNamespace

import shioaji as sj

from backtest.models import OrderStatus
from backtest.shioaji_broker import ShioajiBroker
from tests.unit.test_shioaji_broker import FakeAPI, make_intent, make_order


def test_shioaji_get_order_syncs_fill_price_from_new_fill() -> None:
    api = FakeAPI(status=sj.OrderStatus.Submitted)

    broker = ShioajiBroker(api)
    order = make_order()
    broker.submit_order(order, intent=make_intent(order))

    api.trade.status.status = sj.OrderStatus.Filled
    api.trade.status.deals = [
        SimpleNamespace(
            datetime=make_order().timestamp,
            ts=make_order().timestamp.timestamp(),
            price=20005.0,
            quantity=1,
        )
    ]

    synced_order = broker.get_order("ENTRY-001")

    assert synced_order is not None
    assert synced_order.status == OrderStatus.FILLED
    assert synced_order.fill_price == 20005.0
