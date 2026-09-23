from types import SimpleNamespace

import shioaji as sj

from backtest.shioaji_broker import ShioajiBroker
from tests.unit.test_shioaji_broker import FakeAPI, make_order


def test_shioaji_broker_cancel_order_calls_shioaji() -> None:
    api = FakeAPI(status=sj.OrderStatus.Submitted)

    cancel_calls = []

    def fake_cancel_order(trade):
        cancel_calls.append(trade)
        return trade

    api.cancel_order = fake_cancel_order

    broker = ShioajiBroker(api)

    broker.submit_order(make_order())

    trade = broker._trades["ENTRY-001"]

    api.cancel_order(trade)

    assert cancel_calls == [trade]
