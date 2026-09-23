from __future__ import annotations

from datetime import datetime

from backtest.models import (
    Direction,
    ExitReason,
    Fill,
    Position,
    PositionStatus,
    Signal,
)


class PositionManager:
    def __init__(
        self,
        intrabar_priority: str = "SL_FIRST",
    ):
        allowed = {
            "SL_FIRST",
            "TP_FIRST",
        }

        if intrabar_priority not in allowed:
            raise ValueError(
                f"Unsupported intrabar_priority: "
                f"{intrabar_priority}"
            )

        self.intrabar_priority = intrabar_priority
        self.position: Position | None = None

    @property
    def is_flat(self) -> bool:
        return self.position is None

    @property
    def current_position(self) -> Position | None:
        return self.position

    def open_position(
        self,
        signal: Signal,
        fill: Fill,
    ) -> Position:

        if self.position is not None:
            raise ValueError(
                "Cannot open position: "
                "existing position already exists"
            )

        status = (
            PositionStatus.LONG
            if signal.direction == Direction.LONG
            else PositionStatus.SHORT
        )

        self.position = Position(
            signal_id=signal.signal_id,
            symbol=signal.symbol,
            contract=signal.contract,
            strategy_id=signal.strategy_id,
            strategy_version=signal.strategy_version,
            market_state=signal.market_state,
            setup=signal.setup,
            entry_type=signal.entry_type,
            direction=signal.direction,
            status=status,
            quantity=fill.quantity,
            entry_time=fill.timestamp,
            entry_price=fill.price,
            entry_requested_price=fill.requested_price,
            entry_commission=fill.commission,
            entry_slippage_points=fill.slippage_points,
            stop_price=signal.stop_price,
            target_price=signal.target_price,
            highest_price=fill.price,
            lowest_price=fill.price,
        )

        return self.position

    def add_fill(self, fill: Fill) -> Position:
        if self.position is None:
            raise ValueError(
                "Cannot add fill while position is flat."
            )

        position = self.position

        old_quantity = position.quantity
        new_quantity = old_quantity + fill.quantity

        weighted_entry_price = (
            position.entry_price * old_quantity
            + fill.price * fill.quantity
        ) / new_quantity

        position.quantity = new_quantity
        position.entry_price = weighted_entry_price
        position.entry_commission += fill.commission
        position.entry_slippage_points += fill.slippage_points

        return position

    def reduce_position(self, quantity: int) -> Position | None:
        if self.position is None:
            raise ValueError(
                "Cannot reduce position while flat."
            )

        if quantity <= 0:
            raise ValueError(
                "quantity must be > 0"
            )

        if quantity > self.position.quantity:
            raise ValueError(
                "quantity cannot exceed current position quantity"
            )

        self.position.quantity -= quantity

        if self.position.quantity == 0:
            return self.close_position()

        return self.position

    def update_bar(
        self,
        timestamp: datetime,
        open_price: float,
        high_price: float,
        low_price: float,
        close_price: float,
    ) -> tuple[ExitReason | None, float | None]:

        if self.position is None:
            return None, None

        position = self.position

        if position.highest_price is None:
            position.highest_price = high_price
        else:
            position.highest_price = max(
                position.highest_price,
                high_price,
            )

        if position.lowest_price is None:
            position.lowest_price = low_price
        else:
            position.lowest_price = min(
                position.lowest_price,
                low_price,
            )

        if position.direction == Direction.LONG:
            return self._check_long_exit(
                high_price=high_price,
                low_price=low_price,
            )

        if position.direction == Direction.SHORT:
            return self._check_short_exit(
                high_price=high_price,
                low_price=low_price,
            )

        raise ValueError(
            f"Unsupported direction: {position.direction}"
        )

    def _check_long_exit(
        self,
        high_price: float,
        low_price: float,
    ) -> tuple[ExitReason | None, float | None]:

        position = self.position

        if position is None:
            return None, None

        sl_hit = (
            position.stop_price is not None
            and low_price <= position.stop_price
        )

        tp_hit = (
            position.target_price is not None
            and high_price >= position.target_price
        )

        if sl_hit and tp_hit:
            if self.intrabar_priority == "SL_FIRST":
                return ExitReason.SL, position.stop_price

            return ExitReason.TP, position.target_price

        if sl_hit:
            return ExitReason.SL, position.stop_price

        if tp_hit:
            return ExitReason.TP, position.target_price

        return None, None

    def _check_short_exit(
        self,
        high_price: float,
        low_price: float,
    ) -> tuple[ExitReason | None, float | None]:

        position = self.position

        if position is None:
            return None, None

        sl_hit = (
            position.stop_price is not None
            and high_price >= position.stop_price
        )

        tp_hit = (
            position.target_price is not None
            and low_price <= position.target_price
        )

        if sl_hit and tp_hit:
            if self.intrabar_priority == "SL_FIRST":
                return ExitReason.SL, position.stop_price

            return ExitReason.TP, position.target_price

        if sl_hit:
            return ExitReason.SL, position.stop_price

        if tp_hit:
            return ExitReason.TP, position.target_price

        return None, None

    def close_position(self) -> Position | None:
        position = self.position
        self.position = None
        return position
