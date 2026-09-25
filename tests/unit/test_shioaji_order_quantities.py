import shioaji as sj

from backtest.shioaji_broker import ShioajiBroker
from tests.unit.test_shioaji_broker import FakeAPI, make_intent, make_order


def test_shioaji_order_status_contains_quantity_details() -> None:
    api = FakeAPI(status=sj.OrderStatus.PartFilled)

    api.trade.status.order_quantity = 2
    api.trade.status.deal_quantity = 1
    api.trade.status.cancel_quantity = 0

    broker = ShioajiBroker(api)
    order = make_order()
    broker.submit_order(order, intent=make_intent(order))

    trade = broker._trades["ENTRY-001"]

    assert trade.status.order_quantity == 2
    assert trade.status.deal_quantity == 1
    assert trade.status.cancel_quantity == 0
