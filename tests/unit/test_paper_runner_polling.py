from datetime import date, datetime

from backtest.models import Direction, Signal, SignalAction
from backtest.paper_market_data import PaperMarketDataProvider
from backtest.paper_runner import PaperTradingRunner
from backtest.paper_trading import PaperTradingEngine
from backtest.polling import PollingConfig
from backtest.portfolio import Portfolio
from backtest.position import PositionManager
from backtest.risk import PortfolioRiskManager, RiskConfig
from strategies.base import Strategy


class SequenceStrategy(Strategy):
    name = "SEQUENCE"
    version = "1.0"

    def on_bar(self, bar):
        if bar["close"] == 20000:
            return [
                Signal(
                    signal_id="SIG-001",
                    strategy_id="SEQUENCE",
                    timestamp=bar["timestamp"],
                    trade_date=bar["trade_date"],
                    symbol="TXF",
                    contract="TXF202601",
                    timeframe="1m",
                    strategy_name=self.name,
                    strategy_version=self.version,
                    action=SignalAction.ENTER,
                    direction=Direction.LONG,
                    setup="TEST",
                    entry_type="MARKET",
                    entry_price=bar["close"],
                    stop_loss=None,
                    take_profit=None,
                    quantity=1,
                )
            ]

        return []


def test_paper_runner_run_processes_multiple_iterations():
    bars = [
        {
            "timestamp": datetime(2026, 1, 5, 9, 0),
            "trade_date": date(2026, 1, 5),
            "close": 20000,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 1),
            "trade_date": date(2026, 1, 5),
            "close": 20010,
        },
    ]

    market_data = PaperMarketDataProvider(bars)

    engine = PaperTradingEngine(
        portfolio=Portfolio(
            initial_capital=100000,
            multiplier=200,
        ),
        position_manager=PositionManager(),
        risk_manager=PortfolioRiskManager(
            RiskConfig(
                initial_margin_per_contract=50000,
                maintenance_margin_per_contract=25000,
                max_contracts=1,
                max_margin_utilization=1.0,
            )
        ),
    )

    runner = PaperTradingRunner(
        market_data=market_data,
        strategy=SequenceStrategy(),
        trading_engine=engine,
    )

    result = runner.run(
        config=PollingConfig(interval_seconds=0.001),
        max_iterations=2,
    )

    assert result.iterations == 2
    assert len(result.results) == 2
    assert result.results[0].signals[0].action == SignalAction.ENTER
    assert result.results[0].positions[0].direction == Direction.LONG
    assert result.results[1].signals == []

def test_paper_runner_syncs_pending_orders_before_processing_next_bar():
    from backtest.broker import Broker
    from backtest.execution_result import OrderSubmission
    from backtest.models import Fill, Order, OrderStatus

    class PendingEntryBroker(Broker):
        def __init__(self):
            self.orders: dict[str, Order] = {}
            self.fills: dict[str, list[Fill]] = {}
            self.sync_ready = False

        def submit_order(self, order: Order) -> OrderSubmission:
            submitted_order = order.model_copy(
                update={"status": OrderStatus.SUBMITTED}
            )
            self.orders[order.order_id] = submitted_order
            return OrderSubmission(
                order=submitted_order,
                fills=[],
            )

        def get_order(self, order_id: str) -> Order | None:
            order = self.orders.get(order_id)
            if order is None:
                return None

            if self.sync_ready:
                return order.model_copy(
                    update={"status": OrderStatus.FILLED}
                )

            return order

        def get_fills(self, order_id: str) -> list[Fill]:
            if not self.sync_ready:
                return []

            order = self.orders[order_id]

            fill = Fill(
                order_id=order_id,
                timestamp=order.timestamp,
                requested_price=order.requested_price or 20000.0,
                price=20000.0,
                quantity=order.quantity,
                commission=0.0,
                slippage_points=0.0,
            )

            self.fills[order_id] = [fill]
            return self.fills[order_id]

        def cancel_order(self, order_id: str) -> Order:
            order = self.orders[order_id]
            cancelled = order.model_copy(
                update={"status": OrderStatus.CANCELLED}
            )
            self.orders[order_id] = cancelled
            return cancelled

    class EnterOnceStrategy(Strategy):
        name = "ENTER_ONCE"
        version = "1.0"

        def __init__(self):
            self.called = 0

        def on_bar(self, bar):
            self.called += 1

            if self.called == 1:
                return [
                    Signal(
                        signal_id="SIG-PENDING",
                        strategy_id="ENTER_ONCE",
                        timestamp=bar["timestamp"],
                        trade_date=bar["trade_date"],
                        symbol="TXF",
                        contract="TXF202601",
                        timeframe="1m",
                        strategy_name=self.name,
                        strategy_version=self.version,
                        action=SignalAction.ENTER,
                        direction=Direction.LONG,
                        setup="TEST",
                        entry_type="MARKET",
                        entry_price=bar["close"],
                        stop_loss=None,
                        take_profit=None,
                        quantity=1,
                    )
                ]

            return []

    bars = [
        {
            "timestamp": datetime(2026, 1, 5, 9, 0),
            "trade_date": date(2026, 1, 5),
            "close": 20000,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 1),
            "trade_date": date(2026, 1, 5),
            "close": 20010,
        },
    ]

    broker = PendingEntryBroker()

    engine = PaperTradingEngine(
        broker=broker,
        portfolio=Portfolio(
            initial_capital=100000,
            multiplier=200,
        ),
        position_manager=PositionManager(),
        risk_manager=PortfolioRiskManager(
            RiskConfig(
                initial_margin_per_contract=50000,
                maintenance_margin_per_contract=25000,
                max_contracts=1,
                max_margin_utilization=1.0,
            )
        ),
    )

    runner = PaperTradingRunner(
        market_data=PaperMarketDataProvider(bars),
        strategy=EnterOnceStrategy(),
        trading_engine=engine,
    )

    first = runner.process_latest()

    assert first.positions == [None]
    assert len(engine.pending_orders) == 1

    broker.sync_ready = True

    second = runner.process_latest()

    assert second.signals == []
    assert engine.pending_orders == {}
    assert engine.position_manager.current_position is not None
    assert engine.position_manager.current_position.quantity == 1

def test_paper_runner_syncs_pending_exit_before_next_strategy_bar():
    from backtest.broker import Broker
    from backtest.execution_result import OrderSubmission
    from backtest.models import Fill, Order, OrderStatus

    class PendingExitBroker(Broker):
        def __init__(self):
            self.orders: dict[str, Order] = {}
            self.fills: dict[str, list[Fill]] = {}
            self.exit_ready = False

        def submit_order(self, order: Order) -> OrderSubmission:
            if order.direction == Direction.SHORT:
                submitted_order = order.model_copy(
                    update={"status": OrderStatus.SUBMITTED}
                )
                self.orders[order.order_id] = submitted_order
                return OrderSubmission(
                    order=submitted_order,
                    fills=[],
                )

            submitted_order = order.model_copy(
                update={"status": OrderStatus.FILLED}
            )
            self.orders[order.order_id] = submitted_order

            fill = Fill(
                order_id=order.order_id,
                timestamp=order.timestamp,
                requested_price=order.requested_price or 20000.0,
                price=20000.0,
                quantity=order.quantity,
                commission=0.0,
                slippage_points=0.0,
            )

            self.fills[order.order_id] = [fill]

            return OrderSubmission(
                order=submitted_order,
                fills=[fill],
            )

        def get_order(self, order_id: str) -> Order | None:
            order = self.orders.get(order_id)

            if order is None:
                return None

            if order.direction == Direction.SHORT and self.exit_ready:
                return order.model_copy(
                    update={"status": OrderStatus.FILLED}
                )

            return order

        def get_fills(self, order_id: str) -> list[Fill]:
            if order_id not in self.orders:
                return []

            order = self.orders[order_id]

            if order.direction == Direction.SHORT and not self.exit_ready:
                return []

            if order_id not in self.fills:
                self.fills[order_id] = [
                    Fill(
                        order_id=order_id,
                        timestamp=order.timestamp,
                        requested_price=order.requested_price or 20000.0,
                        price=20100.0,
                        quantity=order.quantity,
                        commission=0.0,
                        slippage_points=0.0,
                    )
                ]

            return self.fills[order_id]

        def cancel_order(self, order_id: str) -> Order:
            order = self.orders[order_id]
            cancelled = order.model_copy(
                update={"status": OrderStatus.CANCELLED}
            )
            self.orders[order_id] = cancelled
            return cancelled

    class EnterThenExitStrategy(Strategy):
        name = "ENTER_THEN_EXIT"
        version = "1.0"

        def __init__(self):
            self.called = 0

        def on_bar(self, bar):
            self.called += 1

            if self.called == 1:
                return [
                    Signal(
                        signal_id="SIG-ENTRY",
                        strategy_id="ENTER_THEN_EXIT",
                        timestamp=bar["timestamp"],
                        trade_date=bar["trade_date"],
                        symbol="TXF",
                        contract="TXF202601",
                        timeframe="1m",
                        strategy_name=self.name,
                        strategy_version=self.version,
                        action=SignalAction.ENTER,
                        direction=Direction.LONG,
                        setup="TEST",
                        entry_type="MARKET",
                        entry_price=bar["close"],
                        stop_loss=None,
                        take_profit=None,
                        quantity=1,
                    )
                ]

            if self.called == 2:
                return [
                    Signal(
                        signal_id="SIG-EXIT",
                        strategy_id="ENTER_THEN_EXIT",
                        timestamp=bar["timestamp"],
                        trade_date=bar["trade_date"],
                        symbol="TXF",
                        contract="TXF202601",
                        timeframe="1m",
                        strategy_name=self.name,
                        strategy_version=self.version,
                        action=SignalAction.EXIT,
                        direction=Direction.SHORT,
                        setup="TEST",
                        entry_type="MARKET",
                        entry_price=bar["close"],
                        stop_loss=None,
                        take_profit=None,
                        quantity=1,
                    )
                ]

            return []

    bars = [
        {
            "timestamp": datetime(2026, 1, 5, 9, 0),
            "trade_date": date(2026, 1, 5),
            "close": 20000,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 1),
            "trade_date": date(2026, 1, 5),
            "close": 20010,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 2),
            "trade_date": date(2026, 1, 5),
            "close": 20100,
        },
    ]

    broker = PendingExitBroker()

    engine = PaperTradingEngine(
        broker=broker,
        portfolio=Portfolio(
            initial_capital=100000,
            multiplier=200,
        ),
        position_manager=PositionManager(),
        risk_manager=PortfolioRiskManager(
            RiskConfig(
                initial_margin_per_contract=50000,
                maintenance_margin_per_contract=25000,
                max_contracts=1,
                max_margin_utilization=1.0,
            )
        ),
    )

    runner = PaperTradingRunner(
        market_data=PaperMarketDataProvider(bars),
        strategy=EnterThenExitStrategy(),
        trading_engine=engine,
    )

    first = runner.process_latest()

    assert first.positions[0] is not None
    assert engine.position_manager.current_position is not None

    second = runner.process_latest()

    assert second.realized_pnl == [None]
    assert len(engine.pending_orders) == 1
    assert engine.position_manager.current_position is not None

    broker.exit_ready = True

    third = runner.process_latest()

    assert third.signals == []
    assert engine.pending_orders == {}
    assert engine.position_manager.current_position is None


def test_paper_runner_full_entry_exit_lifecycle():
    from backtest.paper_broker import PaperBroker

    class FullLifecycleStrategy(Strategy):
        name = "FULL_LIFECYCLE"
        version = "1.0"

        def __init__(self):
            self.called = 0

        def on_bar(self, bar):
            self.called += 1

            if self.called == 1:
                return [
                    Signal(
                        signal_id="SIG-FULL-ENTRY",
                        strategy_id="FULL_LIFECYCLE",
                        timestamp=bar["timestamp"],
                        trade_date=bar["trade_date"],
                        symbol="TXF",
                        contract="TXF202601",
                        timeframe="1m",
                        strategy_name=self.name,
                        strategy_version=self.version,
                        action=SignalAction.ENTER,
                        direction=Direction.LONG,
                        setup="TEST",
                        entry_type="MARKET",
                        entry_price=bar["close"],
                        stop_loss=None,
                        take_profit=None,
                        quantity=1,
                    )
                ]

            if self.called == 2:
                return [
                    Signal(
                        signal_id="SIG-FULL-EXIT",
                        strategy_id="FULL_LIFECYCLE",
                        timestamp=bar["timestamp"],
                        trade_date=bar["trade_date"],
                        symbol="TXF",
                        contract="TXF202601",
                        timeframe="1m",
                        strategy_name=self.name,
                        strategy_version=self.version,
                        action=SignalAction.EXIT,
                        direction=Direction.SHORT,
                        setup="TEST",
                        entry_type="MARKET",
                        entry_price=bar["close"],
                        stop_loss=None,
                        take_profit=None,
                        quantity=1,
                    )
                ]

            return []

    bars = [
        {
            "timestamp": datetime(2026, 1, 5, 9, 0),
            "trade_date": date(2026, 1, 5),
            "close": 20000,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 1),
            "trade_date": date(2026, 1, 5),
            "close": 20100,
        },
    ]

    broker = PaperBroker()

    engine = PaperTradingEngine(
        broker=broker,
        portfolio=Portfolio(
            initial_capital=100000,
            multiplier=200,
        ),
        position_manager=PositionManager(),
        risk_manager=PortfolioRiskManager(
            RiskConfig(
                initial_margin_per_contract=50000,
                maintenance_margin_per_contract=25000,
                max_contracts=1,
                max_margin_utilization=1.0,
            )
        ),
    )

    runner = PaperTradingRunner(
        market_data=PaperMarketDataProvider(bars),
        strategy=FullLifecycleStrategy(),
        trading_engine=engine,
    )

    first = runner.process_latest()

    assert first.signals[0].action == SignalAction.ENTER
    assert engine.position_manager.current_position is not None
    assert engine.position_manager.current_position.quantity == 1

    second = runner.process_latest()

    assert second.signals[0].action == SignalAction.EXIT
    assert engine.position_manager.current_position is None
    assert engine.pending_orders == {}
    assert second.realized_pnl == [20000.0]

def test_paper_runner_full_partial_entry_lifecycle():
    from backtest.broker import Broker
    from backtest.execution_result import OrderSubmission
    from backtest.models import Fill, OrderStatus

    class PartialEntryBroker(Broker):
        def __init__(self):
            self.orders: dict[str, Order] = {}
            self.fills: dict[str, list[Fill]] = {}
            self.completed = False

        def submit_order(self, order: Order) -> OrderSubmission:
            submitted = order.model_copy(
                update={"status": OrderStatus.SUBMITTED}
            )
            self.orders[order.order_id] = submitted

            return OrderSubmission(
                order=submitted,
                fills=[],
            )

        def get_order(self, order_id: str) -> Order | None:
            order = self.orders.get(order_id)

            if order is None:
                return None

            if self.completed:
                return order.model_copy(
                    update={"status": OrderStatus.FILLED}
                )

            return order.model_copy(
                update={"status": OrderStatus.PARTIALLY_FILLED}
            )

        def get_fills(self, order_id: str) -> list[Fill]:
            order = self.orders[order_id]

            if not self.completed:
                fill = Fill(
                    order_id=order_id,
                    timestamp=order.timestamp,
                    requested_price=order.requested_price or 20000.0,
                    price=20000.0,
                    quantity=1,
                    commission=0.0,
                    slippage_points=0.0,
                )
                self.fills[order_id] = [fill]
                return [fill]

            fill = Fill(
                order_id=order_id,
                timestamp=order.timestamp,
                requested_price=order.requested_price or 20000.0,
                price=20010.0,
                quantity=1,
                commission=0.0,
                slippage_points=0.0,
            )
            self.fills[order_id] = [fill]
            return [fill]

        def cancel_order(self, order_id: str) -> Order:
            order = self.orders[order_id]
            cancelled = order.model_copy(
                update={"status": OrderStatus.CANCELLED}
            )
            self.orders[order_id] = cancelled
            return cancelled

    class EnterOnceStrategy(Strategy):
        name = "PARTIAL_ENTRY"
        version = "1.0"

        def __init__(self):
            self.called = 0

        def on_bar(self, bar):
            self.called += 1

            if self.called == 1:
                return [
                    Signal(
                        signal_id="SIG-PARTIAL",
                        strategy_id="PARTIAL_ENTRY",
                        timestamp=bar["timestamp"],
                        trade_date=bar["trade_date"],
                        symbol="TXF",
                        contract="TXF202601",
                        timeframe="1m",
                        strategy_name=self.name,
                        strategy_version=self.version,
                        action=SignalAction.ENTER,
                        direction=Direction.LONG,
                        setup="TEST",
                        entry_type="MARKET",
                        entry_price=bar["close"],
                        stop_loss=None,
                        take_profit=None,
                        quantity=2,
                    )
                ]

            return []

    bars = [
        {
            "timestamp": datetime(2026, 1, 5, 9, 0),
            "trade_date": date(2026, 1, 5),
            "close": 20000,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 1),
            "trade_date": date(2026, 1, 5),
            "close": 20010,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 2),
            "trade_date": date(2026, 1, 5),
            "close": 20020,
        },
    ]

    broker = PartialEntryBroker()

    engine = PaperTradingEngine(
        broker=broker,
        portfolio=Portfolio(
            initial_capital=100000,
            multiplier=200,
        ),
        position_manager=PositionManager(),
        risk_manager=PortfolioRiskManager(
            RiskConfig(
                initial_margin_per_contract=50000,
                maintenance_margin_per_contract=25000,
                max_contracts=2,
                max_margin_utilization=1.0,
            )
        ),
    )

    runner = PaperTradingRunner(
        market_data=PaperMarketDataProvider(bars),
        strategy=EnterOnceStrategy(),
        trading_engine=engine,
    )

    first = runner.process_latest()

    assert first.positions == [None]
    assert len(engine.pending_orders) == 1

    second = runner.process_latest()

    position = engine.position_manager.current_position

    assert position is not None
    assert position.quantity == 1
    assert len(engine.pending_orders) == 1

    broker.completed = True

    third = runner.process_latest()

    position = engine.position_manager.current_position

    assert position is not None
    assert position.quantity == 2
    assert engine.pending_orders == {}

    assert engine.portfolio is not None
    assert engine.portfolio.position is not None
    assert engine.portfolio.position.quantity == 2
    assert engine.portfolio.position.entry_price == 20005.0


def test_paper_runner_full_partial_exit_lifecycle():
    from backtest.broker import Broker
    from backtest.execution_result import OrderSubmission
    from backtest.models import Fill, OrderStatus

    class PartialExitBroker(Broker):
        def __init__(self):
            self.orders: dict[str, Order] = {}
            self.completed = False
            self.exit_order_id: str | None = None
            self.exit_fill_stage = 0

        def submit_order(self, order: Order) -> OrderSubmission:
            if order.order_id.startswith("EXIT-"):
                submitted = order.model_copy(
                    update={"status": OrderStatus.SUBMITTED}
                )
                self.orders[order.order_id] = submitted
                self.exit_order_id = order.order_id

                return OrderSubmission(
                    order=submitted,
                    fills=[],
                )

            filled = order.model_copy(
                update={
                    "status": OrderStatus.FILLED,
                    "fill_price": 20000.0,
                }
            )
            self.orders[order.order_id] = filled

            return OrderSubmission(
                order=filled,
                fills=[
                    Fill(
                        order_id=order.order_id,
                        timestamp=order.timestamp,
                        requested_price=order.requested_price or 20000.0,
                        price=20000.0,
                        quantity=2,
                        commission=0.0,
                        slippage_points=0.0,
                    )
                ],
            )

        def get_order(self, order_id: str) -> Order | None:
            order = self.orders.get(order_id)

            if order is None:
                return None

            if order_id == self.exit_order_id and self.completed:
                return order.model_copy(
                    update={"status": OrderStatus.FILLED}
                )

            if order_id == self.exit_order_id:
                return order.model_copy(
                    update={"status": OrderStatus.PARTIALLY_FILLED}
                )

            return order.model_copy(
                update={"status": OrderStatus.FILLED}
            )

        def get_fills(self, order_id: str) -> list[Fill]:
            order = self.orders[order_id]

            if order_id != self.exit_order_id:
                return [
                    Fill(
                        order_id=order_id,
                        timestamp=order.timestamp,
                        requested_price=order.requested_price or 20000.0,
                        price=20000.0,
                        quantity=2,
                        commission=0.0,
                        slippage_points=0.0,
                    )
                ]

            if self.exit_fill_stage == 0:
                self.exit_fill_stage = 1
                return [
                    Fill(
                        order_id=order_id,
                        timestamp=order.timestamp,
                        requested_price=order.requested_price or 20000.0,
                        price=20010.0,
                        quantity=1,
                        commission=0.0,
                        slippage_points=0.0,
                    )
                ]

            if self.completed and self.exit_fill_stage == 1:
                self.exit_fill_stage = 2
                return [
                    Fill(
                        order_id=order_id,
                        timestamp=order.timestamp,
                        requested_price=order.requested_price or 20000.0,
                        price=20020.0,
                        quantity=1,
                        commission=0.0,
                        slippage_points=0.0,
                    )
                ]

            return []

        def cancel_order(self, order_id: str) -> Order:
            order = self.orders[order_id]
            cancelled = order.model_copy(
                update={"status": OrderStatus.CANCELLED}
            )
            self.orders[order_id] = cancelled
            return cancelled

    class EnterThenExitStrategy(Strategy):
        name = "PARTIAL_EXIT"
        version = "1.0"

        def __init__(self):
            self.called = 0

        def on_bar(self, bar):
            self.called += 1

            if self.called == 1:
                return [
                    Signal(
                        signal_id="SIG-ENTRY",
                        strategy_id="PARTIAL_EXIT",
                        timestamp=bar["timestamp"],
                        trade_date=bar["trade_date"],
                        symbol="TXF",
                        contract="TXF202601",
                        timeframe="1m",
                        strategy_name=self.name,
                        strategy_version=self.version,
                        action=SignalAction.ENTER,
                        direction=Direction.LONG,
                        setup="TEST",
                        entry_type="MARKET",
                        entry_price=bar["close"],
                        stop_loss=None,
                        take_profit=None,
                        quantity=2,
                    )
                ]

            if self.called == 2:
                return [
                    Signal(
                        signal_id="SIG-EXIT",
                        strategy_id="PARTIAL_EXIT",
                        timestamp=bar["timestamp"],
                        trade_date=bar["trade_date"],
                        symbol="TXF",
                        contract="TXF202601",
                        timeframe="1m",
                        strategy_name=self.name,
                        strategy_version=self.version,
                        action=SignalAction.EXIT,
                        direction=Direction.LONG,
                        setup="TEST",
                        entry_type="MARKET",
                        entry_price=bar["close"],
                        stop_loss=None,
                        take_profit=None,
                        quantity=2,
                    )
                ]

            return []

    bars = [
        {
            "timestamp": datetime(2026, 1, 5, 9, 0),
            "trade_date": date(2026, 1, 5),
            "close": 20000,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 1),
            "trade_date": date(2026, 1, 5),
            "close": 20010,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 2),
            "trade_date": date(2026, 1, 5),
            "close": 20020,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 3),
            "trade_date": date(2026, 1, 5),
            "close": 20030,
        },
    ]

    broker = PartialExitBroker()

    engine = PaperTradingEngine(
        broker=broker,
        portfolio=Portfolio(
            initial_capital=100000,
            multiplier=200,
        ),
        position_manager=PositionManager(),
        risk_manager=PortfolioRiskManager(
            RiskConfig(
                initial_margin_per_contract=50000,
                maintenance_margin_per_contract=25000,
                max_contracts=2,
                max_margin_utilization=1.0,
            )
        ),
    )

    runner = PaperTradingRunner(
        market_data=PaperMarketDataProvider(bars),
        strategy=EnterThenExitStrategy(),
        trading_engine=engine,
    )

    first = runner.process_latest()

    position = engine.position_manager.current_position
    assert position is not None
    assert position.quantity == 2
    assert first.positions[0] is not None

    second = runner.process_latest()

    assert second.realized_pnl == [None]
    assert len(engine.pending_orders) == 1

    position = engine.position_manager.current_position
    assert position is not None
    assert position.quantity == 2

    third = runner.process_latest()

    position = engine.position_manager.current_position
    assert position is not None
    assert position.quantity == 1
    assert len(engine.pending_orders) == 1

    broker.completed = True

    fourth = runner.process_latest()

    assert fourth.realized_pnl == []
    assert engine.position_manager.current_position is None
    assert engine.pending_orders == {}

    assert engine.portfolio is not None
    assert engine.portfolio.position is None
    assert engine.portfolio.realized_pnl == 6000.0

