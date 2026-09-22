from __future__ import annotations

from datetime import datetime

from backtest.models import Order, OrderStatus, OrderType, Signal


class OrderFactory:
    @staticmethod
    def create_entry_order(
        signal: Signal,
        timestamp: datetime,
        requested_price: float,
    ) -> Order:
        return Order(
            order_id=f"ENTRY-{signal.signal_id}",
            signal_id=signal.signal_id,
            timestamp=timestamp,
            symbol=signal.symbol,
            contract=signal.contract,
            direction=signal.direction,
            order_type=OrderType.MARKET,
            quantity=signal.quantity,
            requested_price=requested_price,
            status=OrderStatus.PENDING,
        )

    @staticmethod
    def create_exit_order(
        signal: Signal,
        timestamp: datetime,
        requested_price: float,
        quantity: int,
    ) -> Order:
        return Order(
            order_id=f"EXIT-{signal.signal_id}",
            signal_id=signal.signal_id,
            timestamp=timestamp,
            symbol=signal.symbol,
            contract=signal.contract,
            direction=signal.direction,
            order_type=OrderType.MARKET,
            quantity=quantity,
            requested_price=requested_price,
            status=OrderStatus.PENDING,
        )
