from backtest.models import OrderStatus


def test_order_status_has_submitted_state():
    assert OrderStatus.SUBMITTED.value == "SUBMITTED"
