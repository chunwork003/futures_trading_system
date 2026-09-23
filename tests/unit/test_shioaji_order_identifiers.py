from types import SimpleNamespace

import shioaji as sj

from backtest.shioaji_broker import ShioajiBroker
from tests.unit.test_shioaji_broker import FakeAPI, make_order


def test_shioaji_trade_contains_broker_identifiers() -> None:
    api = FakeAPI(status=sj.OrderStatus.Submitted)

    api.trade.order.id = "SHIOAJI-ID-001"
    api.trade.order.seqno = "SEQ-001"
    api.trade.order.ordno = "ORD-001"

    broker = ShioajiBroker(api)
    broker.submit_order(make_order())

    trade = broker._trades["ENTRY-001"]

    assert trade.order.id == "SHIOAJI-ID-001"
    assert trade.order.seqno == "SEQ-001"
    assert trade.order.ordno == "ORD-001"
