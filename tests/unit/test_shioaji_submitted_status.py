import shioaji as sj

from backtest.models import OrderStatus
from backtest.shioaji_mapping import to_order_status


def test_shioaji_pending_submit_maps_to_submitted():
    assert (
        to_order_status(sj.OrderStatus.PendingSubmit)
        == OrderStatus.SUBMITTED
    )


def test_shioaji_pre_submitted_maps_to_submitted():
    assert (
        to_order_status(sj.OrderStatus.PreSubmitted)
        == OrderStatus.SUBMITTED
    )


def test_shioaji_submitted_maps_to_submitted():
    assert (
        to_order_status(sj.OrderStatus.Submitted)
        == OrderStatus.SUBMITTED
    )
