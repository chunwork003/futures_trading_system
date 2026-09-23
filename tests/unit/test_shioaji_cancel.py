import shioaji as sj

from backtest.models import OrderStatus
from backtest.shioaji_broker import ShioajiBroker
from tests.unit.test_shioaji_broker import FakeAPI, make_order


def test_shioaji_broker_cancel_order_updates_status() -> None:
    api = FakeAPI(status=sj.OrderStatus.Cancelled)
    broker = ShioajiBroker(api)

    broker.submit_order(make_order())

    cancelled_order = broker.cancel_order("ENTRY-001")

    assert cancelled_order.order_id == "ENTRY-001"
    assert cancelled_order.status == OrderStatus.CANCELLED
