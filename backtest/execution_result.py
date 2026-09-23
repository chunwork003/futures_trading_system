from __future__ import annotations

from dataclasses import dataclass

from backtest.models import Fill, Order


@dataclass(frozen=True)
class OrderSubmission:
    order: Order
    fills: list[Fill]
