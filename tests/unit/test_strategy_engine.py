from datetime import datetime

import pytest

from backtest.models import Direction, SignalAction
from strategies.config import StrategyParameters
from strategies.registry import create_default_registry
from strategies.trend_state import TrendStateStrategy
from strategies.validation import validate_signal


def make_row(
    timestamp: datetime,
    trend_state: str,
    close: float,
) -> dict:
    return {
        "timestamp": timestamp,
        "trade_date": timestamp.date(),
        "symbol": "TXF",
        "contract": "TXFR1",
        "timeframe": "1m",
        "open": close,
        "high": close + 1,
        "low": close - 1,
        "close": close,
        "volume": 100,
        "trend_state": trend_state,
    }


def test_strategy_parameters_validate():
    params = StrategyParameters(
        symbol="TXF",
        timeframe="1m",
        quantity=1,
    )

    assert params.symbol == "TXF"
    assert params.quantity == 1


def test_strategy_parameters_reject_invalid_quantity():
    with pytest.raises(ValueError):
        StrategyParameters(
            symbol="TXF",
            quantity=0,
        )


def test_trend_state_strategy_generates_long_on_up_transition():
    strategy = TrendStateStrategy(symbol="TXF")

    t1 = datetime(2026, 1, 5, 9, 0)
    t2 = datetime(2026, 1, 5, 9, 1)

    assert strategy.on_bar(
        make_row(t1, "SIDEWAYS", 30000)
    ) == []

    signals = strategy.on_bar(
        make_row(t2, "UP", 30010)
    )

    assert len(signals) == 1
    signal = signals[0]

    assert signal.action == SignalAction.ENTER
    assert signal.direction == Direction.LONG
    assert signal.entry_price == 30010
    assert signal.setup == "TREND_STATE_UP"


def test_trend_state_strategy_generates_short_on_down_transition():
    strategy = TrendStateStrategy(symbol="TXF")

    t1 = datetime(2026, 1, 5, 9, 0)
    t2 = datetime(2026, 1, 5, 9, 1)

    strategy.on_bar(make_row(t1, "UP", 30000))

    signals = strategy.on_bar(
        make_row(t2, "DOWN", 29900)
    )

    assert len(signals) == 1
    assert signals[0].direction == Direction.SHORT


def test_trend_state_strategy_does_not_repeat_signal():
    strategy = TrendStateStrategy(symbol="TXF")

    t1 = datetime(2026, 1, 5, 9, 0)
    t2 = datetime(2026, 1, 5, 9, 1)
    t3 = datetime(2026, 1, 5, 9, 2)

    assert len(
        strategy.on_bar(make_row(t1, "UP", 30000))
    ) == 1

    assert len(
        strategy.on_bar(make_row(t2, "UP", 30010))
    ) == 0

    assert len(
        strategy.on_bar(make_row(t3, "UP", 30020))
    ) == 0


def test_strategy_reset():
    strategy = TrendStateStrategy(symbol="TXF")

    t1 = datetime(2026, 1, 5, 9, 0)

    assert len(
        strategy.on_bar(make_row(t1, "UP", 30000))
    ) == 1

    strategy.reset()

    assert len(
        strategy.on_bar(make_row(t1, "UP", 30000))
    ) == 1


def test_signal_validation():
    strategy = TrendStateStrategy(symbol="TXF")

    timestamp = datetime(2026, 1, 5, 9, 0)

    signal = strategy.on_bar(
        make_row(timestamp, "UP", 30000)
    )[0]

    assert validate_signal(signal) == signal


def test_default_strategy_registry():
    registry = create_default_registry()

    assert registry.contains("EMA_CROSS")
    assert registry.contains("TREND_STATE")

    strategy = registry.create(
        "TREND_STATE",
        symbol="TXF",
    )

    assert isinstance(strategy, TrendStateStrategy)


def test_unknown_strategy_rejected():
    registry = create_default_registry()

    with pytest.raises(KeyError):
        registry.create(
            "UNKNOWN",
            symbol="TXF",
        )
