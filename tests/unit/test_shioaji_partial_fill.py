from types import SimpleNamespace

import shioaji as sj

from backtest.execution_result import OrderSubmission
from backtest.models import OrderStatus
from backtest.shioaji_broker import ShioajiBroker
from tests.unit.test_shioaji_broker import FakeAPI, make_order


def test_shioaji_broker_submit_order_returns_partial_fill() -> None:
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
                )
            ],
        )
    )

    api.place_order = lambda contract, order: trade

    broker = ShioajiBroker(api)

    result = broker.submit_order(
        make_order().model_copy(update={"quantity": 2})
    )

    assert isinstance(result, OrderSubmission)
    assert result.order.status == OrderStatus.PARTIALLY_FILLED
    assert result.order.quantity == 2
    assert len(result.fills) == 1
    assert result.fills[0].quantity == 1
