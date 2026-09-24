from backtest.position_sizing import PositionSizingInput, PositionSizingStrategy


class DummySizingStrategy(PositionSizingStrategy):
    def calculate(self, sizing_input: PositionSizingInput) -> int:
        return 1


def test_position_sizing_strategy_calculate_returns_quantity():
    strategy = DummySizingStrategy()

    sizing_input = PositionSizingInput(
        equity=1_000_000,
        price=20_000,
        stop_price=19_900,
        multiplier=200,
        risk_budget=0.01,
    )

    assert strategy.calculate(sizing_input) == 1
