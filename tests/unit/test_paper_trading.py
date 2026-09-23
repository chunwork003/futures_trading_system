from __future__ import annotations

from datetime import date, datetime

import pytest

from backtest.execution_result import OrderSubmission
from backtest.models import (
    Direction,
    Fill,
    Order,
    OrderStatus,
    OrderType,
    Signal,
)
from backtest.paper_broker import PaperBroker
from backtest.paper_trading import PaperTradingEngine, PendingOrder
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
    broker: PaperBroker | None = None,
    max_contracts: int = 2,
    max_margin_utilization: float = 1.0,
) -> PaperTradingEngine:
    return PaperTradingEngine(
        broker=broker or PaperBroker(),
        position_manager=PositionManager(),
        portfolio=Portfolio(
            initial_capital=100_000,
            multiplier=200,
        ),
        risk_manager=PortfolioRiskManager(
            RiskConfig(
                initial_margin_per_contract=50_000,
                maintenance_margin_per_contract=25_000,
                max_contracts=max_contracts,
                max_margin_utilization=max_margin_utilization,
            )
        ),
    )


def test_paper_trading_engine_submits_order() -> None:
    engine = make_engine()

    submission = engine.submit_order(make_order())

    assert isinstance(submission, OrderSubmission)
    assert submission.order.order_id == "ORD-001"
    assert submission.order.status == OrderStatus.FILLED
    assert len(submission.fills) == 1
    assert submission.fills[0].order_id == "ORD-001"
    assert submission.fills[0].price == 20_000.0
    assert submission.fills[0].quantity == 1


def test_paper_trading_engine_submits_unfilled_order() -> None:
    class SubmittedBroker(PaperBroker):
        def submit_order(self, order: Order) -> OrderSubmission:
            submitted_order = order.model_copy(
                update={"status": OrderStatus.SUBMITTED}
            )
            self.orders[order.order_id] = submitted_order
            self._fills[order.order_id] = []
            return OrderSubmission(
                order=submitted_order,
                fills=[],
            )

    engine = PaperTradingEngine(
        broker=SubmittedBroker(),
        portfolio=Portfolio(
            initial_capital=100_000,
            multiplier=200,
        ),
    )

    submission = engine.submit_order(make_order())

    assert submission.order.status == OrderStatus.SUBMITTED
    assert submission.fills == []


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


def test_paper_trading_engine_closes_position_and_realizes_pnl() -> None:
    engine = make_engine()

    engine.open_position(
        signal=make_signal(),
        order=make_order(),
    )

    exit_order = make_order().model_copy(
        update={
            "order_id": "ORD-002",
            "direction": Direction.SHORT,
            "requested_price": 20_100.0,
        }
    )

    pnl = engine.close_position(exit_order)

    assert pnl == 20_000.0
    assert engine.position_manager.current_position is None
    assert engine.portfolio is not None
    assert engine.portfolio.position is None
    assert engine.portfolio.realized_pnl == 20_000.0


def test_paper_trading_engine_accumulates_multiple_entry_fills() -> None:
    class MultiFillBroker(PaperBroker):
        def submit_order(self, order: Order) -> OrderSubmission:
            first_fill = Fill(
                order_id=order.order_id,
                timestamp=order.timestamp,
                requested_price=20_000.0,
                price=20_000.0,
                quantity=1,
                commission=10.0,
                slippage_points=0.0,
            )
            second_fill = Fill(
                order_id=order.order_id,
                timestamp=order.timestamp,
                requested_price=20_010.0,
                price=20_010.0,
                quantity=1,
                commission=10.0,
                slippage_points=0.0,
            )
            submitted_order = order.model_copy(
                update={
                    "status": OrderStatus.FILLED,
                    "fill_price": 20_005.0,
                }
            )
            return OrderSubmission(
                order=submitted_order,
                fills=[first_fill, second_fill],
            )

    engine = make_engine(
        broker=MultiFillBroker(),
    )

    position = engine.open_position(
        signal=make_signal(),
        order=make_order(),
    )

    assert position.quantity == 2
    assert position.entry_price == 20_005.0
    assert position.entry_commission == 20.0

    assert engine.portfolio is not None
    assert engine.portfolio.position is not None
    assert engine.portfolio.position.quantity == 2
    assert engine.portfolio.position.entry_price == 20_005.0


def test_paper_trading_engine_closes_position_from_multiple_exit_fills() -> None:
    class MultiFillExitBroker(PaperBroker):
        def submit_order(self, order: Order) -> OrderSubmission:
            if order.order_id == "ORD-001":
                return super().submit_order(order)

            first_fill = Fill(
                order_id=order.order_id,
                timestamp=order.timestamp,
                requested_price=20_100.0,
                price=20_100.0,
                quantity=1,
                commission=10.0,
                slippage_points=0.0,
            )
            second_fill = Fill(
                order_id=order.order_id,
                timestamp=order.timestamp,
                requested_price=20_110.0,
                price=20_110.0,
                quantity=1,
                commission=10.0,
                slippage_points=0.0,
            )
            submitted_order = order.model_copy(
                update={
                    "status": OrderStatus.FILLED,
                    "fill_price": 20_105.0,
                }
            )
            return OrderSubmission(
                order=submitted_order,
                fills=[first_fill, second_fill],
            )

    engine = make_engine(
        broker=MultiFillExitBroker(),
    )

    engine.open_position(
        signal=make_signal().model_copy(update={"quantity": 2}),
        order=make_order().model_copy(update={"quantity": 2}),
    )

    exit_order = make_order().model_copy(
        update={
            "order_id": "ORD-002",
            "direction": Direction.SHORT,
            "quantity": 2,
            "requested_price": 20_100.0,
        }
    )

    pnl = engine.close_position(exit_order)

    assert pnl == 41_980.0
    assert engine.position_manager.current_position is None
    assert engine.portfolio is not None
    assert engine.portfolio.position is None
    assert engine.portfolio.realized_pnl == 41_980.0


def test_paper_trading_engine_keeps_position_after_partial_exit_fill() -> None:
    class PartialExitBroker(PaperBroker):
        def submit_order(self, order: Order) -> OrderSubmission:
            if order.order_id == "ORD-001":
                return super().submit_order(order)

            fill = Fill(
                order_id=order.order_id,
                timestamp=order.timestamp,
                requested_price=20_100.0,
                price=20_100.0,
                quantity=1,
                commission=10.0,
                slippage_points=0.0,
            )
            submitted_order = order.model_copy(
                update={
                    "status": OrderStatus.PARTIALLY_FILLED,
                    "fill_price": 20_100.0,
                }
            )
            return OrderSubmission(
                order=submitted_order,
                fills=[fill],
            )

    engine = make_engine(
        broker=PartialExitBroker(),
    )

    engine.open_position(
        signal=make_signal().model_copy(update={"quantity": 2}),
        order=make_order().model_copy(update={"quantity": 2}),
    )

    exit_order = make_order().model_copy(
        update={
            "order_id": "ORD-002",
            "direction": Direction.SHORT,
            "quantity": 2,
            "requested_price": 20_100.0,
        }
    )

    pnl = engine.close_position(exit_order)

    assert pnl == 19_990.0

    assert engine.position_manager.current_position is not None
    assert engine.position_manager.current_position.quantity == 1

    assert engine.portfolio is not None
    assert engine.portfolio.position is not None
    assert engine.portfolio.position.quantity == 1
    assert engine.portfolio.realized_pnl == 19_990.0

def test_paper_trading_engine_apply_entry_fills() -> None:
    engine = make_engine()

    fills = [
        Fill(
            order_id="ORD-001",
            timestamp=datetime(2024, 1, 2, 9, 0),
            requested_price=20_000.0,
            price=20_000.0,
            quantity=1,
            commission=10.0,
            slippage_points=0.0,
        ),
        Fill(
            order_id="ORD-001",
            timestamp=datetime(2024, 1, 2, 9, 0),
            requested_price=20_010.0,
            price=20_010.0,
            quantity=1,
            commission=10.0,
            slippage_points=0.0,
        ),
    ]

    position = engine.apply_entry_fills(
        signal=make_signal().model_copy(update={"quantity": 2}),
        fills=fills,
    )

    assert position.quantity == 2
    assert position.entry_price == 20_005.0
    assert position.entry_commission == 20.0

    assert engine.portfolio is not None
    assert engine.portfolio.position is not None
    assert engine.portfolio.position.quantity == 2
    assert engine.portfolio.position.entry_price == 20_005.0


def test_paper_trading_engine_apply_exit_fills() -> None:
    engine = make_engine()

    engine.open_position(
        signal=make_signal().model_copy(update={"quantity": 2}),
        order=make_order().model_copy(update={"quantity": 2}),
    )

    fills = [
        Fill(
            order_id="ORD-002",
            timestamp=datetime(2024, 1, 2, 9, 1),
            requested_price=20_100.0,
            price=20_100.0,
            quantity=1,
            commission=10.0,
            slippage_points=0.0,
        ),
        Fill(
            order_id="ORD-002",
            timestamp=datetime(2024, 1, 2, 9, 1),
            requested_price=20_110.0,
            price=20_110.0,
            quantity=1,
            commission=10.0,
            slippage_points=0.0,
        ),
    ]

    pnl = engine.apply_exit_fills(fills=fills)

    assert pnl == 41_980.0
    assert engine.position_manager.current_position is None

    assert engine.portfolio is not None
    assert engine.portfolio.position is None
    assert engine.portfolio.realized_pnl == 41_980.0

def test_paper_trading_engine_tracks_pending_order() -> None:
    engine = make_engine()
    signal = make_signal()
    order = make_order()

    engine._pending_orders[order.order_id] = PendingOrder(
        order=order,
        signal=signal,
    )

    pending = engine.pending_orders[order.order_id]

    assert pending.order.order_id == order.order_id
    assert pending.signal is signal


class PendingPaperBroker(PaperBroker):
    def submit_order(self, order: Order) -> OrderSubmission:
        submitted_order = order.model_copy(
            update={"status": OrderStatus.SUBMITTED}
        )
        self.orders[order.order_id] = submitted_order
        self._fills[order.order_id] = []
        return OrderSubmission(
            order=submitted_order,
            fills=[],
        )


def test_paper_trading_engine_open_position_tracks_unfilled_order() -> None:
    engine = make_engine(
        broker=PendingPaperBroker(),
    )
    signal = make_signal()
    order = make_order()

    result = engine.open_position(
        signal=signal,
        order=order,
    )

    assert result is None
    assert order.order_id in engine.pending_orders
    assert engine.pending_orders[order.order_id].order == order
    assert engine.pending_orders[order.order_id].signal is signal

class FillablePendingPaperBroker(PendingPaperBroker):
    def complete_order(
        self,
        order_id: str,
        fills: list[Fill],
        status: OrderStatus = OrderStatus.FILLED,
    ) -> None:
        self._fills[order_id] = fills
        self.orders[order_id] = self.orders[order_id].model_copy(
            update={"status": status}
        )



def test_paper_trading_engine_keeps_pending_order_after_partial_fill() -> None:
    broker = FillablePendingPaperBroker()
    engine = make_engine(
        broker=broker,
    )
    signal = make_signal()
    order = make_order().model_copy(
        update={"quantity": 2}
    )

    result = engine.open_position(
        signal=signal,
        order=order,
    )

    assert result is None
    assert order.order_id in engine.pending_orders

    fill = Fill(
        order_id=order.order_id,
        timestamp=order.timestamp,
        requested_price=order.requested_price,
        price=order.requested_price,
        quantity=1,
        commission=0.0,
        slippage_points=0.0,
    )

    broker.complete_order(
        order_id=order.order_id,
        fills=[fill],
        status=OrderStatus.PARTIALLY_FILLED,
    )

    position = engine.sync_pending_order(
        order_id=order.order_id,
    )

    assert position is not None
    assert position.quantity == 1
    assert order.order_id in engine.pending_orders

def test_paper_trading_engine_syncs_pending_entry_fills() -> None:
    broker = FillablePendingPaperBroker()
    engine = make_engine(broker=broker)
    signal = make_signal()
    order = make_order()

    result = engine.open_position(
        signal=signal,
        order=order,
    )

    assert result is None
    assert order.order_id in engine.pending_orders

    fill = Fill(
        order_id=order.order_id,
        timestamp=order.timestamp,
        requested_price=order.requested_price,
        price=order.requested_price,
        quantity=order.quantity,
        commission=0.0,
        slippage_points=0.0,
    )

    broker.complete_order(
        order_id=order.order_id,
        fills=[fill],
        status=OrderStatus.FILLED,
    )

    position = engine.sync_pending_order(
        order_id=order.order_id,
    )

    assert position is not None
    assert position.quantity == order.quantity
    assert position.entry_price == fill.price
    assert order.order_id not in engine.pending_orders
