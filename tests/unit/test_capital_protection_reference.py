from backtest.capital_protection_reference import CapitalProtectionReference
from backtest.capital_reference_method import CapitalReferenceMethod


def test_capital_protection_reference_accepts_moving_peak():
    reference = CapitalProtectionReference(
        method=CapitalReferenceMethod.MOVING_PEAK,
        reference_equity=1_100_000,
    )

    assert reference.method == CapitalReferenceMethod.MOVING_PEAK
    assert reference.reference_equity == 1_100_000
