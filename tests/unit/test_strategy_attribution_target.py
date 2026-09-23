from backtest.models import Direction
from backtest.strategy_attribution import StrategyAttribution
from backtest.target_position import TargetAccountPosition


def test_strategy_attribution_contributions_match_target_position():
    attributions = [
        StrategyAttribution(
            strategy_id="LONG-TERM",
            symbol="TXF",
            contract="TX1",
            direction=Direction.LONG,
            quantity=2,
        ),
        StrategyAttribution(
            strategy_id="SHORT-TERM",
            symbol="TXF",
            contract="TX1",
            direction=Direction.LONG,
            quantity=1,
        ),
    ]

    target = TargetAccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=sum(
            attribution.quantity
            for attribution in attributions
        ),
    )

    assert target.symbol == "TXF"
    assert target.contract == "TX1"
    assert target.direction == Direction.LONG
    assert target.quantity == 3
