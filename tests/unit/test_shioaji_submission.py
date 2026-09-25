from types import SimpleNamespace

import shioaji as sj

from backtest.execution_result import OrderSubmission
from tests.unit.test_shioaji_broker import FakeAPI, make_intent, make_order
from backtest.shioaji_broker import ShioajiBroker


def test_shioaji_broker_submit_order_returns_submission_without_fill() -> None:
    api = FakeAPI()

    trade = SimpleNamespace(
        status=SimpleNamespace(
            status=sj.OrderStatus.Submitted,
            deals=[],
        )
    )

    api.place_order = lambda contract, order: trade

    broker = ShioajiBroker(api)

    order = make_order()
    result = broker.submit_order(order, intent=make_intent(order))

    assert isinstance(result, OrderSubmission)
    assert result.order.order_id == "ENTRY-001"
    assert result.order.status.value == "SUBMITTED"
    assert result.fills == []
