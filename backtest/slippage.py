class SlippageModel:

    def __init__(self, ticks: int = 0):
        self.ticks = ticks

    def apply(
        self,
        price: float,
        tick_size: float,
        side: str,
    ) -> float:

        adjustment = self.ticks * tick_size

        if side.upper() == "BUY":
            return price + adjustment

        return price - adjustment