from __future__ import annotations

from datetime import datetime
from typing import Iterable

from backtest.models import Signal


REQUIRED_SIGNAL_FIELDS = (
    "signal_id",
    "timestamp",
    "symbol",
    "timeframe",
    "strategy_id",
    "strategy_version",
    "action",
    "direction",
    "entry_price",
    "quantity",
)


def validate_signal(signal: Signal) -> Signal:
    """Validate one strategy signal."""

    if not signal.signal_id:
        raise ValueError("signal_id must not be empty")

    if not isinstance(signal.timestamp, datetime):
        raise ValueError("timestamp must be datetime")

    if not signal.symbol:
        raise ValueError("symbol must not be empty")

    if not signal.timeframe:
        raise ValueError("timeframe must not be empty")

    if not signal.strategy_id:
        raise ValueError("strategy_id must not be empty")

    if not signal.strategy_version:
        raise ValueError("strategy_version must not be empty")

    if signal.entry_price <= 0:
        raise ValueError("entry_price must be greater than zero")

    if signal.quantity <= 0:
        raise ValueError("quantity must be greater than zero")

    return signal


def validate_signals(signals: Iterable[Signal]) -> list[Signal]:
    """Validate and materialize a collection of signals."""

    result = list(signals)

    for signal in result:
        validate_signal(signal)

    return result
