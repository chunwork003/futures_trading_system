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
