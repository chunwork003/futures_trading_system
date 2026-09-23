from backtest.models import Direction
from backtest.strategy_attribution import StrategyAttribution
from backtest.target_position import TargetAccountPosition


def test_target_account_position_preserves_strategy_attributions():
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
        quantity=3,
        attributions=attributions,
    )

    assert target.quantity == 3
    assert target.attributions == attributions
    assert [item.strategy_id for item in target.attributions] == [
        "LONG-TERM",
        "SHORT-TERM",
    ]
