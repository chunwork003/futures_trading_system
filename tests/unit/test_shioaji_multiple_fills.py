from types import SimpleNamespace

import shioaji as sj

from backtest.shioaji_broker import ShioajiBroker
from tests.unit.test_shioaji_broker import FakeAPI, make_intent, make_order


def test_shioaji_broker_get_fills_returns_all_deals() -> None:
    api = FakeAPI(status=sj.OrderStatus.PartFilled)

    trade = SimpleNamespace(
        status=SimpleNamespace(
            status=sj.OrderStatus.PartFilled,
            deals=[
                SimpleNamespace(
                    datetime=make_order().timestamp,
                    ts=make_order().timestamp.timestamp(),
                    price=20001.0,
                    quantity=1,
                seq="TEST-DEAL-003",
                ),
                SimpleNamespace(
                    datetime=make_order().timestamp,
                    ts=make_order().timestamp.timestamp(),
                    price=20002.0,
                    quantity=1,
                seq="TEST-DEAL-004",
                ),
            ],
        )
    )

    api.place_order = lambda contract, order: trade

    broker = ShioajiBroker(api)

    order = make_order().model_copy(update={"quantity": 2})
    submission = broker.submit_order(order, intent=make_intent(order))

    fills = submission.fills

    assert len(fills) == 2
    assert fills[0].quantity == 1
    assert fills[1].quantity == 1
    assert fills[0].price == 20001.0
    assert fills[1].price == 20002.0
