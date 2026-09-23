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
            "open": 20000,
            "high": 20000,
            "low": 20000,
            "close": 20000,
            "volume": 1,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 1),
            "trade_date": date(2026, 1, 5),
            "open": 20010,
            "high": 20010,
            "low": 20010,
            "close": 20010,
            "volume": 1,
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
            "open": 20000,
            "high": 20000,
            "low": 20000,
            "close": 20000,
            "volume": 1,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 1),
            "trade_date": date(2026, 1, 5),
            "open": 20010,
            "high": 20010,
            "low": 20010,
            "close": 20010,
            "volume": 1,
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
            "open": 20000,
            "high": 20000,
            "low": 20000,
            "close": 20000,
            "volume": 1,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 1),
            "trade_date": date(2026, 1, 5),
            "open": 20010,
            "high": 20010,
            "low": 20010,
            "close": 20010,
            "volume": 1,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 2),
            "trade_date": date(2026, 1, 5),
            "open": 20100,
            "high": 20100,
            "low": 20100,
            "close": 20100,
            "volume": 1,
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
            "open": 20000,
            "high": 20000,
            "low": 20000,
            "close": 20000,
            "volume": 1,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 1),
            "trade_date": date(2026, 1, 5),
            "open": 20100,
            "high": 20100,
            "low": 20100,
            "close": 20100,
            "volume": 1,
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
            "open": 20000,
            "high": 20000,
            "low": 20000,
            "close": 20000,
            "volume": 1,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 1),
            "trade_date": date(2026, 1, 5),
            "open": 20010,
            "high": 20010,
            "low": 20010,
            "close": 20010,
            "volume": 1,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 2),
            "trade_date": date(2026, 1, 5),
            "open": 20020,
            "high": 20020,
            "low": 20020,
            "close": 20020,
            "volume": 1,
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
            "open": 20000,
            "high": 20000,
            "low": 20000,
            "close": 20000,
            "volume": 1,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 1),
            "trade_date": date(2026, 1, 5),
            "open": 20010,
            "high": 20010,
            "low": 20010,
            "close": 20010,
            "volume": 1,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 2),
            "trade_date": date(2026, 1, 5),
            "open": 20020,
            "high": 20020,
            "low": 20020,
            "close": 20020,
            "volume": 1,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 3),
            "trade_date": date(2026, 1, 5),
            "open": 20030,
            "high": 20030,
            "low": 20030,
            "close": 20030,
            "volume": 1,
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



def test_paper_runner_full_short_lifecycle():
    from backtest.paper_broker import PaperBroker

    class ShortLifecycleStrategy(Strategy):
        name = "SHORT_LIFECYCLE"
        version = "1.0"

        def __init__(self):
            self.called = 0

        def on_bar(self, bar):
            self.called += 1

            if self.called == 1:
                return [
                    Signal(
                        signal_id="short-entry",
                        timestamp=bar["timestamp"],
                        trade_date=bar["timestamp"].date(),
                        symbol="TXF",
                        timeframe="1m",
                        strategy_id=self.name,
                        strategy_name=self.name,
                        strategy_version=self.version,
                        action=SignalAction.ENTER,
                        direction=Direction.SHORT,
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
                        signal_id="short-exit",
                        timestamp=bar["timestamp"],
                        trade_date=bar["timestamp"].date(),
                        symbol="TXF",
                        timeframe="1m",
                        strategy_id=self.name,
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
            "timestamp": datetime(2026, 1, 1, 9, 0),
            "trade_date": date(2026, 1, 1),
            "symbol": "TXF",
            "open": 20000,
            "high": 20000,
            "low": 20000,
            "close": 20000,
            "volume": 1,
        },
        {
            "timestamp": datetime(2026, 1, 1, 9, 1),
            "trade_date": date(2026, 1, 1),
            "symbol": "TXF",
            "open": 19900,
            "high": 19900,
            "low": 19900,
            "close": 19900,
            "volume": 1,
        },
    ]

    engine = PaperTradingEngine(
        broker=PaperBroker(),
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
        strategy=ShortLifecycleStrategy(),
        trading_engine=engine,
    )

    first = runner.process_latest()

    assert first.signals[0].action == SignalAction.ENTER
    assert first.signals[0].direction == Direction.SHORT
    assert engine.position_manager.current_position is not None
    assert engine.position_manager.current_position.direction == Direction.SHORT
    assert engine.position_manager.current_position.quantity == 1

    second = runner.process_latest()

    assert second.signals[0].action == SignalAction.EXIT
    assert second.signals[0].direction == Direction.SHORT
    assert engine.position_manager.current_position is None
    assert engine.pending_orders == {}
    assert engine.portfolio.realized_pnl == 20000.0

def test_paper_runner_full_short_partial_entry_lifecycle():
    from backtest.broker import Broker
    from backtest.market_data_models import MarketBar
    from backtest.execution_result import OrderSubmission
    from backtest.models import Fill, OrderStatus

    class ShortPartialEntryBroker(Broker):
        def __init__(self):
            self.orders: dict[str, Order] = {}
            self.stage = 0

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
            return self.orders.get(order_id)

        def get_fills(self, order_id: str) -> list[Fill]:
            if self.stage == 0:
                return []

            if self.stage == 1:
                self.stage = 2
                return [
                    Fill(
                        order_id=order_id,
                        timestamp=datetime(2026, 1, 1, 9, 1),
                        requested_price=20000.0,
                        price=20000.0,
                        quantity=1,
                        commission=10.0,
                        slippage_points=0.0,
                    )
                ]

            if self.stage == 2:
                self.stage = 3
                self.orders[order_id] = self.orders[order_id].model_copy(
                    update={"status": OrderStatus.FILLED}
                )
                return [
                    Fill(
                        order_id=order_id,
                        timestamp=datetime(2026, 1, 1, 9, 2),
                        requested_price=20000.0,
                        price=20010.0,
                        quantity=1,
                        commission=10.0,
                        slippage_points=0.0,
                    )
                ]

            return []

        def cancel_order(self, order_id: str) -> Order:
            cancelled = self.orders[order_id].model_copy(
                update={"status": OrderStatus.CANCELLED}
            )
            self.orders[order_id] = cancelled
            return cancelled

    class ShortPartialEntryStrategy(Strategy):
        name = "SHORT_PARTIAL_ENTRY"
        version = "1.0"

        def __init__(self):
            self.called = 0

        def on_bar(self, bar):
            self.called += 1

            if self.called == 1:
                return [
                    Signal(
                        signal_id="SIG-SHORT-PARTIAL",
                        strategy_id=self.name,
                        timestamp=bar["timestamp"],
                        trade_date=bar["trade_date"],
                        symbol="TXF",
                        contract="TXF202601",
                        timeframe="1m",
                        strategy_name=self.name,
                        strategy_version=self.version,
                        action=SignalAction.ENTER,
                        direction=Direction.SHORT,
                        setup="TEST",
                        entry_type="MARKET",
                        entry_price=20000.0,
                        quantity=2,
                        stop_price=None,
                        target_price=None,
                        market_state="TREND",
                    )
                ]

            return []

    bars = [
        MarketBar(
            timestamp=datetime(2026, 1, 1, 9, 0),
            trade_date=date(2026, 1, 1),
            symbol="TXF",
            open=20000.0,
            high=20000.0,
            low=20000.0,
            close=20000.0,
            volume=1,
        ),
        MarketBar(
            timestamp=datetime(2026, 1, 1, 9, 1),
            trade_date=date(2026, 1, 1),
            symbol="TXF",
            open=20000.0,
            high=20010.0,
            low=19990.0,
            close=20005.0,
            volume=1,
        ),
        MarketBar(
            timestamp=datetime(2026, 1, 1, 9, 2),
            trade_date=date(2026, 1, 1),
            symbol="TXF",
            open=20005.0,
            high=20010.0,
            low=20000.0,
            close=20005.0,
            volume=1,
        ),
    ]

    broker = ShortPartialEntryBroker()

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
        strategy=ShortPartialEntryStrategy(),
        trading_engine=engine,
    )

    first = runner.process_latest()

    assert first.positions == [None]
    assert len(engine.pending_orders) == 1

    broker.stage = 1
    second = runner.process_latest()

    position = engine.position_manager.current_position

    assert position is not None
    assert position.direction == Direction.SHORT
    assert position.quantity == 1
    assert position.entry_price == 20000.0
    assert len(engine.pending_orders) == 1

    third = runner.process_latest()

    position = engine.position_manager.current_position

    assert position is not None
    assert position.direction == Direction.SHORT
    assert position.quantity == 2
    assert position.entry_price == 20005.0
    assert engine.portfolio.position is not None
    assert engine.portfolio.position.quantity == 2
    assert engine.portfolio.position.entry_price == 20005.0
    assert engine.pending_orders == {}
from datetime import date, datetime


def test_paper_runner_passes_full_market_bar_to_strategy():
    from backtest.paper_broker import PaperBroker
    from backtest.market_data_models import MarketBar
    from backtest.paper_market_data import PaperMarketDataProvider
    from backtest.paper_runner import PaperTradingRunner
    from backtest.paper_trading import PaperTradingEngine
    from backtest.position import PositionManager
    from backtest.portfolio import Portfolio
    from backtest.risk import PortfolioRiskManager, RiskConfig

    class CaptureStrategy:
        name = "CAPTURE"
        version = "1.0"

        def __init__(self):
            self.received_bar = None

        def on_bar(self, bar):
            self.received_bar = bar
            return []

    bar = MarketBar(
        timestamp=datetime(2026, 1, 5, 9, 0),
        trade_date=date(2026, 1, 5),
        symbol="TXF",
        open=20000.0,
        high=20050.0,
        low=19980.0,
        close=20030.0,
        volume=1250,
        amount=25037500.0,
    )

    strategy = CaptureStrategy()

    engine = PaperTradingEngine(
        broker=PaperBroker(),
        position_manager=PositionManager(),
        portfolio=Portfolio(initial_capital=100000, multiplier=200),
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
        market_data=PaperMarketDataProvider([bar]),
        strategy=strategy,
        trading_engine=engine,
    )

    runner.process_latest()

    assert strategy.received_bar["open"] == 20000.0
    assert strategy.received_bar["high"] == 20050.0
    assert strategy.received_bar["low"] == 19980.0
    assert strategy.received_bar["close"] == 20030.0
    assert strategy.received_bar["volume"] == 1250
    assert strategy.received_bar["amount"] == 25037500.0












def test_paper_runner_full_short_partial_exit_lifecycle():
    from backtest.broker import Broker
    from backtest.execution_result import OrderSubmission
    from backtest.models import Fill, OrderStatus

    class ShortPartialExitBroker(Broker):
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
                return []

            if self.exit_fill_stage == 0:
                self.exit_fill_stage = 1
                return [
                    Fill(
                        order_id=order_id,
                        timestamp=order.timestamp,
                        requested_price=order.requested_price or 20000.0,
                        price=19990.0,
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
                        price=19980.0,
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

    class ShortEnterThenExitStrategy(Strategy):
        name = "SHORT_PARTIAL_EXIT"
        version = "1.0"

        def __init__(self):
            self.called = 0

        def on_bar(self, bar):
            self.called += 1

            if self.called == 1:
                return [
                    Signal(
                        signal_id="SIG-SHORT-ENTRY",
                        strategy_id=self.name,
                        timestamp=bar["timestamp"],
                        trade_date=bar["trade_date"],
                        symbol="TXF",
                        contract="TXF202601",
                        timeframe="1m",
                        strategy_name=self.name,
                        strategy_version=self.version,
                        action=SignalAction.ENTER,
                        direction=Direction.SHORT,
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
                        signal_id="SIG-SHORT-EXIT",
                        strategy_id=self.name,
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
                        quantity=2,
                    )
                ]

            return []

    bars = [
        {
            "timestamp": datetime(2026, 1, 5, 9, 0),
            "trade_date": date(2026, 1, 5),
            "symbol": "TXF",
            "open": 20000,
            "high": 20000,
            "low": 20000,
            "close": 20000,
            "volume": 1,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 1),
            "trade_date": date(2026, 1, 5),
            "symbol": "TXF",
            "open": 19990,
            "high": 20000,
            "low": 19980,
            "close": 19990,
            "volume": 1,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 2),
            "trade_date": date(2026, 1, 5),
            "symbol": "TXF",
            "open": 19980,
            "high": 19990,
            "low": 19970,
            "close": 19980,
            "volume": 1,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 3),
            "trade_date": date(2026, 1, 5),
            "symbol": "TXF",
            "open": 19980,
            "high": 19990,
            "low": 19970,
            "close": 19980,
            "volume": 1,
        },
    ]

    broker = ShortPartialExitBroker()

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
        strategy=ShortEnterThenExitStrategy(),
        trading_engine=engine,
    )

    first = runner.process_latest()

    assert first.positions[0] is not None
    assert first.positions[0].direction == Direction.SHORT
    assert first.positions[0].quantity == 2

    second = runner.process_latest()

    position = engine.position_manager.current_position

    assert position is not None
    assert position.direction == Direction.SHORT
    assert position.quantity == 2
    assert len(engine.pending_orders) == 1
    assert second.realized_pnl == [None]

    third = runner.process_latest()

    position = engine.position_manager.current_position

    assert position is not None
    assert position.direction == Direction.SHORT
    assert position.quantity == 1
    assert len(engine.pending_orders) == 1
    assert third.realized_pnl == []

    broker.completed = True

    fourth = runner.process_latest()

    assert engine.position_manager.current_position is None
    assert engine.pending_orders == {}
    assert engine.portfolio is not None
    assert engine.portfolio.position is None
    assert engine.portfolio.realized_pnl == 6000.0
