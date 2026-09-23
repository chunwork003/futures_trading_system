from backtest.strategy_conflict import StrategyConflict


def test_strategy_conflict_records_conflicting_strategies():
    conflict = StrategyConflict(
        symbol="TXF",
        contract="TX1",
        strategy_ids=["LONG-TERM", "SHORT-TERM"],
    )

    assert conflict.symbol == "TXF"
    assert conflict.contract == "TX1"
    assert conflict.strategy_ids == ["LONG-TERM", "SHORT-TERM"]
