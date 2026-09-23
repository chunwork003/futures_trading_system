import shioaji as sj

from backtest.models import OrderStatus
from backtest.shioaji_broker import ShioajiBroker

from tests.unit.test_shioaji_broker import FakeAPI, make_order


def test_get_order_returns_submitted_when_shioaji_order_has_no_fill():
    api = FakeAPI(status=sj.OrderStatus.Submitted)
    broker = ShioajiBroker(api)
    order = make_order()

    broker._orders[order.order_id] = order
    broker._trades[order.order_id] = api.trade

    result = broker.get_order(order.order_id)

    assert result is not None
    assert result.status == OrderStatus.SUBMITTED
