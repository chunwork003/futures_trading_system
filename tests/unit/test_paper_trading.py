from datetime import date, datetime

import pytest

from backtest.models import (
    Direction,
    Order,
    OrderStatus,
    OrderType,
    Signal,
)
from backtest.paper_broker import PaperBroker
from backtest.paper_trading import PaperTradingEngine
from backtest.portfolio import Portfolio
from backtest.position import PositionManager
from backtest.risk import PortfolioRiskManager, RiskConfig


def make_signal() -> Signal:
    return Signal(
        signal_id="SIG-001",
        timestamp=datetime(2026, 1, 5, 9, 0),
        trade_date=date(2026, 1, 5),
        symbol="TXF",
        contract="TXF202601",
        timeframe="1m",
        strategy_id="S1",
        strategy_version="v1",
        action="ENTER",
        direction=Direction.LONG,
        market_state="UPTREND",
        setup="TEST",
        entry_type="MARKET",
        entry_price=20_000.0,
        stop_price=None,
        target_price=None,
        quantity=1,
    )


def make_order() -> Order:
    return Order(
        order_id="ORD-001",
        signal_id="SIG-001",
        timestamp=datetime(2026, 1, 5, 9, 0),
        symbol="TXF",
        contract="TXF202601",
        direction=Direction.LONG,
        order_type=OrderType.MARKET,
        quantity=1,
        requested_price=20_000.0,
        status=OrderStatus.PENDING,
    )


def make_engine(
    *,
    max_margin_utilization: float = 1.0,
) -> PaperTradingEngine:
    return PaperTradingEngine(
        broker=PaperBroker(),
        position_manager=PositionManager(),
        portfolio=Portfolio(
            initial_capital=100_000,
            multiplier=200,
        ),
        risk_manager=PortfolioRiskManager(
            RiskConfig(
                initial_margin_per_contract=50_000,
                maintenance_margin_per_contract=25_000,
                max_contracts=1,
                max_margin_utilization=max_margin_utilization,
            )
        ),
    )


def test_paper_trading_engine_submits_order() -> None:
    engine = make_engine()

    fill = engine.submit_order(make_order())

    assert fill.order_id == "ORD-001"
    assert fill.price == 20_000.0
    assert fill.quantity == 1


def test_paper_trading_engine_rejects_order_by_risk() -> None:
    engine = make_engine(
        max_margin_utilization=0.4,
    )

    with pytest.raises(ValueError, match="risk manager"):
        engine.submit_order(make_order())


def test_paper_trading_engine_opens_position_from_fill() -> None:
    engine = make_engine()

    position = engine.open_position(
        signal=make_signal(),
        order=make_order(),
    )

    assert position.signal_id == "SIG-001"
    assert position.direction == Direction.LONG
    assert position.quantity == 1
    assert position.entry_price == 20_000.0
    assert engine.position_manager.current_position is position
def test_paper_trading_engine_updates_portfolio_on_entry() -> None:
    engine = make_engine()

    position = engine.open_position(
        signal=make_signal(),
        order=make_order(),
    )

    assert position.quantity == 1
    assert engine.portfolio is not None
    assert engine.portfolio.position is not None
    assert engine.portfolio.position.direction == position.direction
    assert engine.portfolio.position.entry_price == position.entry_price
    assert engine.portfolio.position.quantity == position.quantity
    assert engine.portfolio.unrealized_pnl == 0.0

