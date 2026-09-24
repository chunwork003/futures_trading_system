from backtest.capital_reference_strategy import CapitalReferenceStrategy


class DummyCapitalReference(CapitalReferenceStrategy):
    def update(self, equity: float) -> float:
        return equity


def test_capital_reference_strategy_defines_update_contract():
    strategy = DummyCapitalReference()

    assert strategy.update(1_000_000) == 1_000_000
