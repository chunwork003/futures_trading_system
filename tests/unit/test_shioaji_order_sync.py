from types import SimpleNamespace

import shioaji as sj

from backtest.models import OrderStatus
from backtest.shioaji_broker import ShioajiBroker
from tests.unit.test_shioaji_broker import FakeAPI, make_order


def test_shioaji_broker_get_order_updates_fill_price() -> None:
    api = FakeAPI(status=sj.OrderStatus.Filled)

    trade = SimpleNamespace(
        status=SimpleNamespace(
            status=sj.OrderStatus.Filled,
            deals=[
                SimpleNamespace(
                    datetime=make_order().timestamp,
                    ts=make_order().timestamp.timestamp(),
                    price=20005.0,
                    quantity=1,
                seq="TEST-DEAL-005",
                )
            ],
        )
    )

    api.place_order = lambda contract, order: trade

    broker = ShioajiBroker(api)

    broker.submit_order(make_order())

    order = broker.get_order("ENTRY-001")

    assert order is not None
    assert order.status == OrderStatus.FILLED
    assert order.fill_price == 20005.0
