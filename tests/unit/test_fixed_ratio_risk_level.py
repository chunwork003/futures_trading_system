from backtest.fixed_ratio_risk_level import FixedRatioRiskLevel


def test_fixed_ratio_risk_levels_are_defined():
    assert FixedRatioRiskLevel.NORMAL.value == "NORMAL"
    assert FixedRatioRiskLevel.LEVEL_1.value == "LEVEL_1"
    assert FixedRatioRiskLevel.LEVEL_2.value == "LEVEL_2"
    assert FixedRatioRiskLevel.LEVEL_3.value == "LEVEL_3"
