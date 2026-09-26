import shioaji as sj
import pytest

from backtest.models import OrderStatus
from backtest.shioaji_mapping import (
    UnverifiedBrokerOrderStatusError,
    to_order_status,
)


def test_shioaji_pending_submit_maps_to_submitted():
    assert (
        to_order_status(sj.OrderStatus.PendingSubmit)
        == OrderStatus.SUBMITTED
    )


def test_shioaji_pre_submitted_is_capability_unverified():
    with pytest.raises(
        UnverifiedBrokerOrderStatusError
    ) as exc_info:
        to_order_status(sj.OrderStatus.PreSubmitted)

    assert exc_info.value.status is sj.OrderStatus.PreSubmitted
    assert "PreSubmitted" in str(exc_info.value)


def test_shioaji_submitted_maps_to_submitted():
    assert (
        to_order_status(sj.OrderStatus.Submitted)
        == OrderStatus.SUBMITTED
    )
