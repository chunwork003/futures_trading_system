from datetime import date, datetime

from backtest.models import BacktestConfig, Signal
from backtest.multi_strategy import MultiStrategyBacktestRunner
from backtest.risk import RiskConfig
from strategy.multi_runner import MultiStrategyRunner
from strategy.registry import StrategyRegistry


class DummyStrategy:
    def __init__(self, strategy_id: str) -> None:
        self.strategy_id = strategy_id

    def generate_signals(self, bars):
        return [
            Signal(
                signal_id="SIG-01-LONG-ENTER",
                timestamp=datetime(2026, 1, 5, 9, 0),
                trade_date=date(2026, 1, 5),
                symbol="TXF",
                contract="TXF202601",
                timeframe="1m",
                strategy_id=self.strategy_id,
                strategy_version="v1",
                action="ENTER",
                direction="LONG",
                market_state="UPTREND",
                setup="TEST_SETUP",
                entry_type="NEXT_BAR_OPEN",
                entry_price=20_000.0,
                stop_price=None,
                target_price=None,
                quantity=1,
            )
        ]


def test_multi_strategy_risk_blocks_entry_when_margin_limit_is_exceeded() -> None:
    registry = StrategyRegistry()

    registry.register(
        strategy_id="S1",
        version="v1",
        factory=lambda: DummyStrategy("S1"),
    )

    runner = MultiStrategyBacktestRunner(
        MultiStrategyRunner(registry)
    )

    config = BacktestConfig(
        initial_capital=100_000,
        symbol="TXF",
        risk_config=RiskConfig(
            initial_margin_per_contract=60_000,
            maintenance_margin_per_contract=30_000,
            max_contracts=1,
            max_margin_utilization=0.5,
        ),
    )

    bars = [
        {
            "timestamp": datetime(2026, 1, 5, 9, 0),
            "open": 20_000,
            "high": 20_000,
            "low": 20_000,
            "close": 20_000,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 1),
            "open": 20_000,
            "high": 20_000,
            "low": 20_000,
            "close": 20_000,
        },
    ]

    results = runner.run(
        strategy_ids=["S1"],
        bars=bars,
        backtest_config=config,
    )

    assert len(results) == 1
    assert results[0].report.trade_statistics.total_trades == 0
