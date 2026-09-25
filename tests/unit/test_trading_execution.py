import pytest
from pydantic import ValidationError

from trading.account import AccountPosition, PositionDirection
from trading.execution import (
    OrderIntent,
    PositionEffect,
    PositionEffectValidationError,
    validate_position_effect,
)


def _intent(
    *,
    direction: PositionDirection = PositionDirection.LONG,
    effect: PositionEffect = PositionEffect.OPEN,
    quantity: int = 1,
) -> OrderIntent:
    return OrderIntent(
        intent_id=" INT-001 ",
        correlation_id=" CORR-001 ",
        causation_id=" CAUSE-001 ",
        position_direction=direction,
        position_effect=effect,
        quantity=quantity,
        target_position_ref=" TARGET-001 ",
        risk_decision_ref=" RISK-001 ",
    )


def _expected(
    *,
    direction: PositionDirection = PositionDirection.LONG,
    quantity: int = 3,
) -> AccountPosition:
    return AccountPosition(
        broker="SINOPAC",
        account_ref="9A95-1234567",
        instrument_id=1,
        contract_id=101,
        direction=direction,
        quantity=quantity,
    )


def test_position_effect_has_exact_values() -> None:
    assert [effect.value for effect in PositionEffect] == [
        "OPEN",
        "REDUCE",
        "CLOSE",
    ]


def test_order_intent_normalizes_references_and_is_immutable() -> None:
    intent = _intent()

    assert intent.intent_id == "INT-001"
    assert intent.correlation_id == "CORR-001"
    assert intent.causation_id == "CAUSE-001"
    assert intent.target_position_ref == "TARGET-001"
    assert intent.risk_decision_ref == "RISK-001"
    with pytest.raises(ValidationError):
        intent.quantity = 2


@pytest.mark.parametrize(
    "field",
    [
        "intent_id",
        "correlation_id",
        "causation_id",
        "target_position_ref",
        "risk_decision_ref",
    ],
)
def test_order_intent_rejects_blank_references(field: str) -> None:
    values = _intent().model_dump()
    values[field] = "  "
    with pytest.raises(ValidationError, match="must not be blank"):
        OrderIntent(**values)


def test_order_intent_forbids_extra_native_fields() -> None:
    with pytest.raises(ValidationError, match="native_order"):
        OrderIntent(**_intent().model_dump(), native_order=object())


@pytest.mark.parametrize(
    "effect",
    [PositionEffect.REDUCE, PositionEffect.CLOSE],
)
def test_flat_only_allows_open(effect: PositionEffect) -> None:
    with pytest.raises(PositionEffectValidationError, match="only permits OPEN"):
        validate_position_effect(_intent(effect=effect), None)


def test_flat_and_same_direction_open_are_allowed() -> None:
    validate_position_effect(_intent(), None)
    validate_position_effect(_intent(), _expected())


def test_reduce_must_leave_positive_expected_quantity() -> None:
    expected = _expected(quantity=3)

    validate_position_effect(
        _intent(effect=PositionEffect.REDUCE, quantity=2),
        expected,
    )
    for quantity in (3, 4):
        with pytest.raises(PositionEffectValidationError, match="less than"):
            validate_position_effect(
                _intent(effect=PositionEffect.REDUCE, quantity=quantity),
                expected,
            )


def test_close_requires_exact_expected_quantity() -> None:
    expected = _expected(quantity=3)

    validate_position_effect(
        _intent(effect=PositionEffect.CLOSE, quantity=3),
        expected,
    )
    for quantity in (2, 4):
        with pytest.raises(PositionEffectValidationError, match="must equal"):
            validate_position_effect(
                _intent(effect=PositionEffect.CLOSE, quantity=quantity),
                expected,
            )


def test_opposite_direction_is_rejected_without_mutation() -> None:
    expected = _expected()
    before = expected.model_dump()

    with pytest.raises(PositionEffectValidationError, match="confirmed FLAT"):
        validate_position_effect(
            _intent(direction=PositionDirection.SHORT),
            expected,
        )

    assert expected.model_dump() == before
