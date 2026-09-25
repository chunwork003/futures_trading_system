from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from backtest.models import Direction, Signal, SignalAction
from strategies.base import Strategy


class EMACrossStrategy(Strategy):
    strategy_id = "EMA_CROSS"
    strategy_version = "1.0.0"
    state_schema_version = 1

    def __init__(
        self,
        symbol: str,
        timeframe: str = "1m",
        quantity: int = 1,
        stop_price: Optional[float] = None,
        target_price: Optional[float] = None,
    ) -> None:
        if quantity <= 0:
            raise ValueError("quantity must be greater than zero")

        self.symbol = symbol
        self.timeframe = timeframe
        self.quantity = quantity
        self.stop_price = stop_price
        self.target_price = target_price

        self._previous_ema20: Optional[float] = None
        self._previous_ema60: Optional[float] = None

    def on_bar(self, row: dict[str, Any]) -> list[Signal]:
        ema20 = row.get("ema_20")
        ema60 = row.get("ema_60")

        if ema20 is None or ema60 is None:
            self._update_previous_values(ema20, ema60)
            return []

        if self._previous_ema20 is None or self._previous_ema60 is None:
            self._update_previous_values(ema20, ema60)
            return []

        timestamp = self._get_timestamp(row)
        trade_date = self._get_trade_date(row)

        signals: list[Signal] = []

        if (
            self._previous_ema20 <= self._previous_ema60
            and ema20 > ema60
        ):
            signals.append(
                self._build_signal(
                    row=row,
                    timestamp=timestamp,
                    trade_date=trade_date,
                    direction=Direction.LONG,
                )
            )

        elif (
            self._previous_ema20 >= self._previous_ema60
            and ema20 < ema60
        ):
            signals.append(
                self._build_signal(
                    row=row,
                    timestamp=timestamp,
                    trade_date=trade_date,
                    direction=Direction.SHORT,
                )
            )

        self._update_previous_values(ema20, ema60)

        return signals

    def _build_signal(
        self,
        row: dict[str, Any],
        timestamp: datetime,
        trade_date: date,
        direction: Direction,
    ) -> Signal:
        close = row.get("close")

        if close is None:
            raise ValueError("row must contain close")

        signal_id = (
            f"{self.strategy_id}-"
            f"{timestamp.strftime('%Y%m%d%H%M%S')}-"
            f"{direction.value}"
        )

        return Signal(
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
            market_state=row.get("market_state"),
            setup="EMA20_EMA60_CROSS",
            entry_type="NEXT_BAR_OPEN",
            entry_price=float(close),
            stop_price=self.stop_price,
            target_price=self.target_price,
            quantity=self.quantity,
        )

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

        raise ValueError("row must contain trade_date or datetime timestamp")

    def _update_previous_values(
        self,
        ema20: Optional[float],
        ema60: Optional[float],
    ) -> None:
        if ema20 is not None:
            self._previous_ema20 = float(ema20)

        if ema60 is not None:
            self._previous_ema60 = float(ema60)

    def export_state(self) -> dict[str, object]:
        """只匯出明確核准的 EMA crossover state。"""

        return {
            "schema_version": self.state_schema_version,
            "previous_ema20": self._previous_ema20,
            "previous_ema60": self._previous_ema60,
        }

    def restore_state(self, state: dict[str, object]) -> None:
        if set(state) != {"schema_version", "previous_ema20", "previous_ema60"}:
            raise ValueError("invalid EMA_CROSS state fields")
        if state["schema_version"] != self.state_schema_version:
            raise ValueError("EMA_CROSS state schema mismatch")
        for key in ("previous_ema20", "previous_ema60"):
            value = state[key]
            if value is not None and not isinstance(value, (int, float)):
                raise ValueError(f"{key} must be numeric or null")
        self._previous_ema20 = None if state["previous_ema20"] is None else float(state["previous_ema20"])
        self._previous_ema60 = None if state["previous_ema60"] is None else float(state["previous_ema60"])
