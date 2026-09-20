from __future__ import annotations

from datetime import date, datetime
from typing import Any

from backtest.models import Direction, Signal, SignalAction


class TrendStateExitStrategy:
    """
    P5 baseline trend-state strategy with explicit exits.

    Rules:
    - UP transition -> LONG entry.
    - DOWN transition -> SHORT entry.
    - LONG position leaving UP -> EXIT LONG.
    - SHORT position leaving DOWN -> EXIT SHORT.
    - After an exit, a new direction is entered on the next bar
      if the new trend state remains valid.
    """

    strategy_id = "TREND_STATE_EXIT"
    strategy_version = "1.0.0"

    def __init__(
        self,
        symbol: str,
        timeframe: str = "1m",
        quantity: int = 1,
    ) -> None:
        self.symbol = symbol
        self.timeframe = timeframe
        self.quantity = quantity

        self._previous_state: str | None = None
        self._position: Direction | None = None
        self._pending_entry_state: str | None = None

    def reset(self) -> None:
        self._previous_state = None
        self._position = None
        self._pending_entry_state = None

    def on_bar(self, row: dict[str, Any]) -> list[Signal]:
        timestamp = row["timestamp"]
        trade_date = self._get_trade_date(row)
        state = row.get("trend_state")

        if state is None:
            self._previous_state = None
            return []

        state = str(state).upper()
        close = row.get("close")

        if close is None:
            raise ValueError("row must contain close")

        signals: list[Signal] = []

        # 1. Exit current position when its trend state is no longer valid.
        if (
            self._position == Direction.LONG
            and state != "UP"
        ):
            signals.append(
                self._build_signal(
                    timestamp=timestamp,
                    trade_date=trade_date,
                    state=state,
                    action=SignalAction.EXIT,
                    direction=Direction.LONG,
                    setup="TREND_STATE_EXIT_LONG",
                    entry_price=float(close),
                    row=row,
                )
            )

            self._position = None

            if state == "DOWN":
                self._pending_entry_state = "DOWN"

        elif (
            self._position == Direction.SHORT
            and state != "DOWN"
        ):
            signals.append(
                self._build_signal(
                    timestamp=timestamp,
                    trade_date=trade_date,
                    state=state,
                    action=SignalAction.EXIT,
                    direction=Direction.SHORT,
                    setup="TREND_STATE_EXIT_SHORT",
                    entry_price=float(close),
                    row=row,
                )
            )

            self._position = None

            if state == "UP":
                self._pending_entry_state = "UP"

        # 2. Enter a new direction after the previous position has exited.
        if (
            self._position is None
            and self._pending_entry_state == state
            and state in {"UP", "DOWN"}
            and not signals
        ):
            direction = (
                Direction.LONG
                if state == "UP"
                else Direction.SHORT
            )

            signals.append(
                self._build_signal(
                    timestamp=timestamp,
                    trade_date=trade_date,
                    state=state,
                    action=SignalAction.ENTER,
                    direction=direction,
                    setup=f"TREND_STATE_{state}",
                    entry_price=float(close),
                    row=row,
                )
            )

            self._position = direction
            self._pending_entry_state = None

        # 3. Normal entry on transition into UP / DOWN.
        elif (
            self._position is None
            and state in {"UP", "DOWN"}
            and state != self._previous_state
            and not signals
        ):
            direction = (
                Direction.LONG
                if state == "UP"
                else Direction.SHORT
            )

            signals.append(
                self._build_signal(
                    timestamp=timestamp,
                    trade_date=trade_date,
                    state=state,
                    action=SignalAction.ENTER,
                    direction=direction,
                    setup=f"TREND_STATE_{state}",
                    entry_price=float(close),
                    row=row,
                )
            )

            self._position = direction

        self._previous_state = state

        return signals

    def _build_signal(
        self,
        *,
        timestamp: datetime,
        trade_date: date,
        state: str,
        action: SignalAction,
        direction: Direction,
        setup: str,
        entry_price: float,
        row: dict[str, Any],
    ) -> Signal:
        return Signal(
            signal_id=(
                f"{self.strategy_id}-"
                f"{self._timestamp_string(timestamp)}-"
                f"{action.value}-"
                f"{direction.value}"
            ),
            timestamp=timestamp,
            trade_date=trade_date,
            symbol=self.symbol,
            contract=row.get("contract"),
            timeframe=self.timeframe,
            strategy_id=self.strategy_id,
            strategy_version=self.strategy_version,
            action=action,
            direction=direction,
            market_state=state,
            setup=setup,
            entry_type="NEXT_BAR_OPEN",
            entry_price=entry_price,
            quantity=self.quantity,
        )

    @staticmethod
    def _get_trade_date(row: dict[str, Any]) -> date:
        trade_date = row.get("trade_date")

        if isinstance(trade_date, datetime):
            return trade_date.date()

        if isinstance(trade_date, date):
            return trade_date

        timestamp = row.get("timestamp")

        if isinstance(timestamp, datetime):
            return timestamp.date()

        raise ValueError(
            "row must contain trade_date or datetime timestamp"
        )

    @staticmethod
    def _timestamp_string(timestamp: datetime) -> str:
        return timestamp.strftime("%Y%m%d%H%M%S")
