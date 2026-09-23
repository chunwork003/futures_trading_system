from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from backtest.models import Fill


def to_fill(
    order_id: str,
    deal: Any,
    requested_price: float,
    commission: float = 0.0,
    slippage_points: float = 0.0,
) -> Fill:
    timestamp = deal.datetime or datetime.fromtimestamp(
        deal.ts
    )

    return Fill(
        order_id=order_id,
        timestamp=timestamp,
        requested_price=requested_price,
        price=deal.price,
        quantity=deal.quantity,
        commission=commission,
        slippage_points=slippage_points,
    )


def to_fills(
    order_id: str,
    deals: Iterable[Any],
    requested_price: float,
    commission: float = 0.0,
    slippage_points: float = 0.0,
) -> list[Fill]:
    return [
        to_fill(
            order_id=order_id,
            deal=deal,
            requested_price=requested_price,
            commission=commission,
            slippage_points=slippage_points,
        )
        for deal in deals
    ]


def merge_fills(
    fills: Iterable[Fill],
) -> Fill:
    fills = list(fills)

    if not fills:
        raise ValueError("Cannot merge empty fills.")

    total_quantity = sum(fill.quantity for fill in fills)

    weighted_price = sum(
        fill.price * fill.quantity
        for fill in fills
    ) / total_quantity

    return Fill(
        order_id=fills[0].order_id,
        timestamp=max(fill.timestamp for fill in fills),
        requested_price=fills[0].requested_price,
        price=weighted_price,
        quantity=total_quantity,
        commission=sum(fill.commission for fill in fills),
        slippage_points=fills[0].slippage_points,
    )
