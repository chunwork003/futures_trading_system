from backtest.position_sizing import PositionSizingInput, PositionSizingStrategy


class BacktestSizingAdapter:
    def __init__(self, strategy: PositionSizingStrategy) -> None:
        self.strategy = strategy

    def calculate_quantity(
        self,
        sizing_input: PositionSizingInput,
    ) -> int:
        return self.strategy.calculate(sizing_input)
