from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from backtest.models import Direction, Signal, SignalAction
from strategies.base import Strategy
from strategies.config import StrategyParameters
from strategies.validation import validate_signal


class TrendStateStrategy(Strategy):
    """
    Baseline trend-following strategy.

    Entry:
        UP   -> LONG
        DOWN -> SHORT

    A signal is emitted only when the trend state changes
    into UP or DOWN.

    EXIT / REVERSE are intentionally not generated here.
    The current backtest architecture handles one position
    at a time and next-bar execution.
    """

    strategy_id = "TREND_STATE"
    strategy_version = "1.0.0"

    def __init__(
        self,
        symbol: str,
        timeframe: str = "1m",
        quantity: int = 1,
        stop_price: Optional[float] = None,
        target_price: Optional[float] = None,
    ) -> None:
        self.parameters = StrategyParameters(
            symbol=symbol,
            timeframe=timeframe,
            quantity=quantity,
            stop_price=stop_price,
            target_price=target_price,
        )

        self._previous_state: Optional[str] = None

    @property
    def symbol(self) -> str:
        return self.parameters.symbol

    @property
    def timeframe(self) -> str:
        return self.parameters.timeframe

    @property
    def quantity(self) -> int:
        return self.parameters.quantity

    def on_bar(self, row: dict[str, Any]) -> list[Signal]:
        state = row.get("trend_state")

        if state is None:
            self._previous_state = None
            return []

        state = str(state).upper()

        signal: Optional[Signal] = None

        if state in {"UP", "DOWN"} and state != self._previous_state:
            direction = (
                Direction.LONG
                if state == "UP"
                else Direction.SHORT
            )

            signal = self._build_signal(
                row=row,
                direction=direction,
                state=state,
            )

        self._previous_state = state

        if signal is None:
            return []

        return [signal]

    def reset(self) -> None:
        """Reset state before a new backtest run."""

        self._previous_state = None

    def _build_signal(
        self,
        row: dict[str, Any],
        direction: Direction,
        state: str,
    ) -> Signal:
        timestamp = self._get_timestamp(row)
        trade_date = self._get_trade_date(row)

        close = row.get("close")

        if close is None:
            raise ValueError("row must contain close")

        signal_id = (
            f"{self.strategy_id}-"
            f"{timestamp.strftime('%Y%m%d%H%M%S')}-"
            f"{direction.value}"
        )

        signal = Signal(
            signal_id=signal_id,
            timestamp=timestamp,
            trade_date=trade_date,
            symbol=self.symbol,
            contract=row.get("contract"),
            timeframe=self.timeframe,
            strategy_id=self.strategy_id,
            strategy_version=self.strategy_version,
            action=SignalAction.ENTER,
            direction=direction,
            market_state=state,
            setup=f"TREND_STATE_{state}",
            entry_type="NEXT_BAR_OPEN",
            entry_price=float(close),
            stop_price=self.parameters.stop_price,
            target_price=self.parameters.target_price,
            quantity=self.quantity,
        )

        return validate_signal(signal)

    @staticmethod
    def _get_timestamp(row: dict[str, Any]) -> datetime:
        timestamp = row.get("timestamp")

        if not isinstance(timestamp, datetime):
            raise ValueError("row must contain a datetime timestamp")

        return timestamp

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
