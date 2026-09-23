from datetime import datetime, timezone, timedelta

from backtest.models import Fill
from backtest.shioaji_fill import merge_fills


def test_merge_fills_uses_quantity_weighted_price():
    tz = timezone(timedelta(hours=8))

    fills = [
        Fill(
            order_id="ENTRY-001",
            timestamp=datetime(2026, 1, 5, 9, 0, tzinfo=tz),
            requested_price=20000.0,
            price=20000.0,
            quantity=1,
            commission=10.0,
            slippage_points=0.0,
        ),
        Fill(
            order_id="ENTRY-001",
            timestamp=datetime(2026, 1, 5, 9, 0, 1, tzinfo=tz),
            requested_price=20000.0,
            price=20005.0,
            quantity=2,
            commission=20.0,
            slippage_points=0.0,
        ),
    ]

    fill = merge_fills(fills)

    assert fill.order_id == "ENTRY-001"
    assert fill.timestamp == fills[1].timestamp
    assert fill.requested_price == 20000.0
    assert fill.price == 20003.333333333332
    assert fill.quantity == 3
    assert fill.commission == 30.0
    assert fill.slippage_points == 0.0
