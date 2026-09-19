class CommissionModel:

    def __init__(self, rate: float = 0.0):
        self.rate = rate

    def calculate(
        self,
        price: float,
        quantity: int,
        multiplier: float,
    ) -> float:

        turnover = (
            price
            * quantity
            * multiplier
        )

        return turnover * self.rate