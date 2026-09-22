from backtest.models import ExitReason


def test_exit_reason_supports_forced_liquidation():
    assert ExitReason.FORCED_LIQUIDATION.value == "FORCED_LIQUIDATION"
