from __future__ import annotations

from backtest.cost import CostCalculator
from backtest.models import (
    Fill,
    Order,
    OrderStatus,
    OrderType,
)


class ExecutionEngine:
    def __init__(
        self,
        cost_calculator: CostCalculator,
    ):
        self.cost_calculator = cost_calculator

    def execute_market_order(
        self,
        order: Order,
        market_price: float,
        is_entry: bool = True,
    ) -> Fill:

        if order.order_type != OrderType.MARKET:
            raise ValueError(
                "execute_market_order only supports MARKET orders"
            )

        if order.status != OrderStatus.PENDING:
            raise ValueError(
                "Only PENDING orders can be executed"
            )

        cost = self.cost_calculator.calculate_execution_cost(
            requested_price=market_price,
            direction=order.direction,
            quantity=order.quantity,
            is_entry=is_entry,
        )

        return Fill(
            order_id=order.order_id,
            timestamp=order.timestamp,
            requested_price=cost.requested_price,
            price=cost.fill_price,
            quantity=order.quantity,
            commission=cost.commission,
            slippage_points=cost.slippage_points,
        )
