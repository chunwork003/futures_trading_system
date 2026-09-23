from backtest.models import Direction
from backtest.strategy_attribution import StrategyAttribution


def test_strategy_attribution_represents_strategy_contribution():
    attribution = StrategyAttribution(
        strategy_id="LONG-TERM",
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=2,
    )

    assert attribution.strategy_id == "LONG-TERM"
    assert attribution.symbol == "TXF"
    assert attribution.contract == "TX1"
    assert attribution.direction == Direction.LONG
    assert attribution.quantity == 2
