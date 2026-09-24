import pytest

from backtest.fixed_ratio_risk_multipliers import FixedRatioRiskMultipliers


def test_fixed_ratio_risk_multipliers_accept_valid_values():
    multipliers = FixedRatioRiskMultipliers(
        normal=1.0,
        level_1=0.75,
        level_2=0.50,
        level_3=0.25,
    )

    assert multipliers.normal == 1.0
    assert multipliers.level_1 == 0.75
    assert multipliers.level_2 == 0.50
    assert multipliers.level_3 == 0.25


@pytest.mark.parametrize(
    "field",
    ["level_1", "level_2", "level_3"],
)
def test_fixed_ratio_risk_multipliers_allow_zero(field):
    values = {
        "normal": 1.0,
        "level_1": 0.5,
        "level_2": 0.25,
        "level_3": 0.0,
    }

    values[field] = 0.0

    multipliers = FixedRatioRiskMultipliers(**values)

    assert getattr(multipliers, field) == 0.0


def test_normal_multiplier_must_be_greater_than_zero():
    with pytest.raises(ValueError):
        FixedRatioRiskMultipliers(
            normal=0,
            level_1=0.5,
            level_2=0.25,
            level_3=0,
        )


@pytest.mark.parametrize(
    "field",
    ["normal", "level_1", "level_2", "level_3"],
)
def test_multiplier_cannot_exceed_one(field):
    values = {
        "normal": 1.0,
        "level_1": 0.5,
        "level_2": 0.25,
        "level_3": 0.0,
    }

    values[field] = 1.01

    with pytest.raises(ValueError):
        FixedRatioRiskMultipliers(**values)
