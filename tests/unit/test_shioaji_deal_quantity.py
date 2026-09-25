from types import SimpleNamespace

import shioaji as sj

from backtest.shioaji_broker import ShioajiBroker
from tests.unit.test_shioaji_broker import FakeAPI, make_intent, make_order


def test_shioaji_get_fills_matches_deal_quantity() -> None:
    api = FakeAPI(status=sj.OrderStatus.PartFilled)

    order = make_order()

    api.trade.status.order_quantity = 2
    api.trade.status.deal_quantity = 1
    api.trade.status.cancel_quantity = 0
    api.trade.status.deals = [
        SimpleNamespace(
            datetime=order.timestamp,
            ts=order.timestamp.timestamp(),
            price=20005.0,
            quantity=1,
                seq="TEST-DEAL-002",
        )
    ]

    broker = ShioajiBroker(api)
    submission = broker.submit_order(order, intent=make_intent(order))

    fills = submission.fills

    assert sum(fill.quantity for fill in fills) == api.trade.status.deal_quantity
