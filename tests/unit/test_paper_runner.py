from datetime import date, datetime

from backtest.models import Direction, SignalAction
from backtest.paper_broker import PaperBroker
from backtest.paper_market_data import PaperMarketDataProvider
from backtest.paper_runner import PaperTradingRunner
from backtest.paper_trading import PaperTradingEngine
from backtest.portfolio import Portfolio
from backtest.position import PositionManager
from backtest.risk import PortfolioRiskManager, RiskConfig
from strategies.trend_state_exit import TrendStateExitStrategy


def make_engine() -> PaperTradingEngine:
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
                max_margin_utilization=1.0,
            )
        ),
    )


def test_paper_runner_processes_latest_bar():
    bars = [
        {
            "timestamp": datetime(2026, 1, 5, 9, 0),
            "trade_date": date(2026, 1, 5),
            "symbol": "TXF",
            "contract": "TXF202601",
            "open": 20_000,
            "high": 20_000,
            "low": 20_000,
            "close": 20_000,
            "volume": 1,
            "trend_state": "UP",
        }
    ]

    provider = PaperMarketDataProvider(bars)
    strategy = TrendStateExitStrategy(
        symbol="TXF",
        timeframe="1m",
        quantity=1,
    )
    engine = make_engine()
    runner = PaperTradingRunner(
        market_data=provider,
        strategy=strategy,
        trading_engine=engine,
    )

    result = runner.process_latest()

    assert len(result.signals) == 1
    assert result.signals[0].action == SignalAction.ENTER
    assert result.signals[0].direction == Direction.LONG

    assert len(result.orders) == 1
    assert result.orders[0].signal_id == result.signals[0].signal_id
    assert result.orders[0].symbol == "TXF"
    assert result.orders[0].contract == "TXF202601"
    assert result.orders[0].quantity == 1
    assert result.orders[0].requested_price == 20_000

    assert len(result.positions) == 1
    assert result.positions[0].direction == Direction.LONG
    assert result.positions[0].quantity == 1
    assert result.positions[0].entry_price == 20_000

    assert engine.position_manager.current_position is result.positions[0]
    assert engine.portfolio is not None
    assert engine.portfolio.position is not None
    assert engine.portfolio.position.quantity == 1
from datetime import date, datetime

from backtest.models import Direction, SignalAction
from backtest.paper_broker import PaperBroker
from backtest.paper_market_data import PaperMarketDataProvider
from backtest.paper_runner import PaperTradingRunner
from backtest.paper_trading import PaperTradingEngine
from backtest.portfolio import Portfolio
from backtest.position import PositionManager
from backtest.risk import PortfolioRiskManager, RiskConfig
from strategies.trend_state_exit import TrendStateExitStrategy


def make_engine() -> PaperTradingEngine:
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
                max_margin_utilization=1.0,
            )
        ),
    )


def test_paper_runner_entry_then_exit():
    bars = [
        {
            "timestamp": datetime(2026, 1, 5, 9, 0),
            "trade_date": date(2026, 1, 5),
            "symbol": "TXF",
            "contract": "TXF202601",
            "open": 20_000,
            "high": 20_000,
            "low": 20_000,
            "close": 20_000,
            "volume": 1,
            "trend_state": "UP",
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 1),
            "trade_date": date(2026, 1, 5),
            "symbol": "TXF",
            "contract": "TXF202601",
            "open": 20_100,
            "high": 20_100,
            "low": 20_100,
            "close": 20_100,
            "volume": 1,
            "trend_state": "DOWN",
        },
    ]

    provider = PaperMarketDataProvider(bars)
    strategy = TrendStateExitStrategy(
        symbol="TXF",
        timeframe="1m",
        quantity=1,
    )
    engine = make_engine()
    runner = PaperTradingRunner(
        market_data=provider,
        strategy=strategy,
        trading_engine=engine,
    )

    first = runner.process_latest()

    assert len(first.signals) == 1
    assert first.signals[0].action == SignalAction.ENTER
    assert first.signals[0].direction == Direction.LONG
    assert len(first.orders) == 1
    assert len(first.positions) == 1

    second = runner.process_latest()

    assert len(second.signals) == 1
    assert second.signals[0].action == SignalAction.EXIT
    assert second.signals[0].direction == Direction.LONG
    assert len(second.orders) == 1
    assert second.orders[0].order_id == "EXIT-" + second.signals[0].signal_id
    assert second.realized_pnl == [20_000.0]

    assert engine.position_manager.current_position is None
    assert engine.portfolio is not None
    assert engine.portfolio.position is None
    assert engine.portfolio.realized_pnl == 20_000.0

