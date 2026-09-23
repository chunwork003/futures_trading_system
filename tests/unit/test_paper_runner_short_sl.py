from datetime import date, datetime

from backtest.models import Direction, Signal, SignalAction
from backtest.paper_broker import PaperBroker
from backtest.paper_market_data import PaperMarketDataProvider
from backtest.paper_runner import PaperTradingRunner
from backtest.paper_trading import PaperTradingEngine
from backtest.portfolio import Portfolio
from backtest.risk import PortfolioRiskManager, RiskConfig
from strategies.base import Strategy
from backtest.market_data_models import MarketBar


class ShortSLStrategy(Strategy):
    name = "SHORT_SL"
    version = "1.0"

    def __init__(self):
        self.called = False

    def on_bar(self, row):
        if self.called:
            return []

        self.called = True

        return [
            Signal(
                signal_id="SHORT-SL-001",
                timestamp=row["timestamp"],
                trade_date=row["trade_date"],
                strategy_id=self.name,
                strategy_version=self.version,
                symbol="TXF",
                contract="TXF202601",
                timeframe="1m",
                action=SignalAction.ENTER,
                direction=Direction.SHORT,
                quantity=1,
                entry_type="MARKET",
                entry_price=row["close"],
                stop_price=20_100.0,
                target_price=19_800.0,
                market_state="TREND",
            )
        ]


def make_bar(timestamp, open_price, high_price, low_price, close_price):
    return MarketBar(
        timestamp=timestamp,
        trade_date=date(2026, 1, 5),
        symbol="TXF",
        open=open_price,
        high=high_price,
        low=low_price,
        close=close_price,
        volume=1,
    )


def test_short_stop_loss_lifecycle():
    bars = [
        make_bar(
            datetime(2026, 1, 5, 9, 0),
            20_000.0,
            20_000.0,
            20_000.0,
            20_000.0,
        ),
        make_bar(
            datetime(2026, 1, 5, 9, 1),
            20_000.0,
            20_150.0,
            19_950.0,
            20_100.0,
        ),
    ]

    engine = PaperTradingEngine(
        broker=PaperBroker(),
        portfolio=Portfolio(
            initial_capital=100_000,
            multiplier=200,
        ),
        risk_manager=PortfolioRiskManager(
            RiskConfig(max_contracts=1)
        ),
    )

    runner = PaperTradingRunner(
        market_data=PaperMarketDataProvider(bars),
        strategy=ShortSLStrategy(),
        trading_engine=engine,
    )

    first = runner.process_latest()
    assert first.positions[0] is not None
    assert engine.position_manager.current_position is not None
    assert (
        engine.position_manager.current_position.direction
        == Direction.SHORT
    )

    second = runner.process_latest()

    assert second.orders
    assert second.orders[-1].direction == Direction.SHORT
    assert second.realized_pnl == [-20_000.0]
    assert engine.position_manager.current_position is None




def test_short_take_profit_lifecycle():
    bars = [
        make_bar(
            datetime(2026, 1, 5, 9, 0),
            20_000.0,
            20_000.0,
            20_000.0,
            20_000.0,
        ),
        make_bar(
            datetime(2026, 1, 5, 9, 1),
            20_000.0,
            20_050.0,
            19_750.0,
            19_800.0,
        ),
    ]

    engine = PaperTradingEngine(
        broker=PaperBroker(),
        portfolio=Portfolio(
            initial_capital=100_000,
            multiplier=200,
        ),
        risk_manager=PortfolioRiskManager(
            RiskConfig(max_contracts=1)
        ),
    )

    runner = PaperTradingRunner(
        market_data=PaperMarketDataProvider(bars),
        strategy=ShortSLStrategy(),
        trading_engine=engine,
    )

    first = runner.process_latest()

    assert first.positions[0] is not None
    assert engine.position_manager.current_position is not None
    assert (
        engine.position_manager.current_position.direction
        == Direction.SHORT
    )

    second = runner.process_latest()

    assert second.orders
    assert second.orders[-1].direction == Direction.SHORT
    assert second.realized_pnl == [40_000.0]
    assert engine.position_manager.current_position is None


def test_short_sl_tp_same_bar_uses_sl_first():
    bars = [
        make_bar(
            datetime(2026, 1, 5, 9, 0),
            20_000.0,
            20_000.0,
            20_000.0,
            20_000.0,
        ),
        make_bar(
            datetime(2026, 1, 5, 9, 1),
            20_000.0,
            20_150.0,
            19_750.0,
            20_000.0,
        ),
    ]

    engine = PaperTradingEngine(
        broker=PaperBroker(),
        portfolio=Portfolio(
            initial_capital=100_000,
            multiplier=200,
        ),
        risk_manager=PortfolioRiskManager(
            RiskConfig(max_contracts=1)
        ),
    )

    runner = PaperTradingRunner(
        market_data=PaperMarketDataProvider(bars),
        strategy=ShortSLStrategy(),
        trading_engine=engine,
    )

    first = runner.process_latest()

    assert first.positions[0] is not None
    assert engine.position_manager.current_position is not None

    second = runner.process_latest()

    assert second.orders
    assert second.realized_pnl == [-20_000.0]
    assert second.orders[-1].requested_price == 20_100.0
    assert engine.position_manager.current_position is None
