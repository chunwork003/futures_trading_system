from __future__ import annotations

import pytest
from pydantic import ValidationError

from strategy.instance import (
    CanonicalInstrumentBindingProvenance,
    StrategyInstance,
    config_fingerprint,
)
from strategy.recovery import (
    StrategyAuthorityRef,
    StrategyDurableStateReference,
    StrategyGoverningContext,
    StrategyGoverningTransitionAuthority,
    StrategyGoverningTransitionIntegrityError,
    StrategyGoverningTransitionState,
    StrategyStateSchemaReference,
    evaluate_governing_transition,
)


def binding() -> CanonicalInstrumentBindingProvenance:
    return CanonicalInstrumentBindingProvenance(
        instrument_id=101,
        authority_id="CANONICAL-INSTRUMENT-PROVISIONING",
        authority_version="V1",
        reference_id="BIND-C17",
    )


def source_instance() -> StrategyInstance:
    config = {"symbol": "TX", "timeframe": "1m"}
    return StrategyInstance(
        strategy_instance_id="SI-C17",
        strategy_id="EMA_CROSS",
        strategy_version="1.0.0",
        config_version="C1",
        config_fingerprint=config_fingerprint(config),
        instrument_id=101,
        timeframe="1m",
        config_json=config,
        instrument_binding_provenance=binding(),
    )


def context(
    *,
    config_version: str,
    config_fingerprint_value: str,
    policy_version: str,
    schema_version: int,
) -> StrategyGoverningContext:
    return StrategyGoverningContext(
        strategy_instance_id="SI-C17",
        strategy_id="EMA_CROSS",
        config_authority=StrategyAuthorityRef(
            authority_id="STRATEGY-CONFIG",
            authority_version=config_version,
        ),
        config_version=config_version,
        config_fingerprint=config_fingerprint_value,
        implementation_revision="1.0.0",
        instrument_id=101,
        instrument_binding_provenance=binding(),
        timeframe="1m",
        decision_policy_version=policy_version,
        state_schema_reference=StrategyStateSchemaReference(
            strategy_id="EMA_CROSS",
            schema_version=schema_version,
        ),
    )


def state_ref(
    *,
    snapshot_id: str,
    config_version: str,
    config_fingerprint_value: str,
    schema_version: int,
) -> StrategyDurableStateReference:
    return StrategyDurableStateReference(
        snapshot_id=snapshot_id,
        strategy_instance_id="SI-C17",
        strategy_id="EMA_CROSS",
        config_version=config_version,
        config_fingerprint=config_fingerprint_value,
        implementation_revision="1.0.0",
        instrument_id=101,
        timeframe="1m",
        state_schema_reference=StrategyStateSchemaReference(
            strategy_id="EMA_CROSS",
            schema_version=schema_version,
        ),
    )


def authority(
    state: StrategyGoverningTransitionState,
    *,
    established_during_progress: bool = False,
) -> tuple[
    StrategyGoverningTransitionAuthority,
    StrategyDurableStateReference,
    StrategyDurableStateReference,
]:
    instance = source_instance()
    source = context(
        config_version="C1",
        config_fingerprint_value=instance.config_fingerprint,
        policy_version="DP-1",
        schema_version=1,
    )
    target_config = {"symbol": "TX", "timeframe": "1m", "mode": "target"}
    target_fingerprint = config_fingerprint(target_config)
    target = context(
        config_version="C2",
        config_fingerprint_value=target_fingerprint,
        policy_version="DP-2",
        schema_version=2,
    )
    source_state = state_ref(
        snapshot_id="SS-SOURCE",
        config_version="C1",
        config_fingerprint_value=instance.config_fingerprint,
        schema_version=1,
    )
    target_state = state_ref(
        snapshot_id="SS-TARGET",
        config_version="C2",
        config_fingerprint_value=target_fingerprint,
        schema_version=2,
    )

    values = dict(
        transition_id="TR-C17",
        strategy_instance_id="SI-C17",
        source_context=source,
        target_context=target,
        compatibility_authority=StrategyAuthorityRef(
            authority_id="STRATEGY-COMPATIBILITY",
            authority_version="V1",
        ),
        migration_authority=StrategyAuthorityRef(
            authority_id="STATE-MIGRATION",
            authority_version="V1",
        ),
        transition_policy=StrategyAuthorityRef(
            authority_id="GOVERNING-TRANSITION",
            authority_version="V1",
        ),
    )

    if state is StrategyGoverningTransitionState.TRANSITION_IN_PROGRESS:
        values["begin_effective_boundary_ref"] = "BOUNDARY-BEGIN-1"
        if established_during_progress:
            values["established_target_state"] = target_state
    elif state is StrategyGoverningTransitionState.POST_TRANSITION:
        values["begin_effective_boundary_ref"] = "BOUNDARY-BEGIN-1"
        values["completion_boundary_ref"] = "BOUNDARY-COMPLETE-1"
        values["established_target_state"] = target_state

    return (
        StrategyGoverningTransitionAuthority(**values),
        source_state,
        target_state,
    )


def test_c17_has_exactly_three_conceptual_states() -> None:
    assert tuple(
        item.value for item in StrategyGoverningTransitionState
    ) == (
        "PRE_TRANSITION",
        "TRANSITION_IN_PROGRESS",
        "POST_TRANSITION",
    )


def test_pre_transition_uses_source_context_and_durable_state() -> None:
    item, source_state, _ = authority(
        StrategyGoverningTransitionState.PRE_TRANSITION
    )

    assert item.state is StrategyGoverningTransitionState.PRE_TRANSITION
    assert (
        evaluate_governing_transition(
            authority=item,
            source_instance=source_instance(),
            durable_state=source_state,
        )
        is StrategyGoverningTransitionState.PRE_TRANSITION
    )


def test_in_progress_is_classified_only_from_durable_boundary() -> None:
    item, source_state, _ = authority(
        StrategyGoverningTransitionState.TRANSITION_IN_PROGRESS
    )

    assert (
        evaluate_governing_transition(
            authority=item,
            source_instance=source_instance(),
            durable_state=source_state,
        )
        is StrategyGoverningTransitionState.TRANSITION_IN_PROGRESS
    )


def test_in_progress_may_have_staged_target_state_but_is_not_post_transition() -> None:
    item, _, target_state = authority(
        StrategyGoverningTransitionState.TRANSITION_IN_PROGRESS,
        established_during_progress=True,
    )

    assert (
        evaluate_governing_transition(
            authority=item,
            source_instance=source_instance(),
            durable_state=target_state,
        )
        is StrategyGoverningTransitionState.TRANSITION_IN_PROGRESS
    )


def test_post_transition_requires_exact_target_compatible_durable_state() -> None:
    item, _, target_state = authority(
        StrategyGoverningTransitionState.POST_TRANSITION
    )

    assert (
        evaluate_governing_transition(
            authority=item,
            source_instance=source_instance(),
            durable_state=target_state,
        )
        is StrategyGoverningTransitionState.POST_TRANSITION
    )

    wrong = target_state.model_copy(
        update={"snapshot_id": "OTHER"}
    )

    with pytest.raises(
        StrategyGoverningTransitionIntegrityError,
        match="target-compatible durable state",
    ):
        evaluate_governing_transition(
            authority=item,
            source_instance=source_instance(),
            durable_state=wrong,
        )


def test_mixed_completion_without_begin_or_target_state_fails_closed() -> None:
    pre, _, _ = authority(
        StrategyGoverningTransitionState.PRE_TRANSITION
    )

    with pytest.raises(ValidationError):
        StrategyGoverningTransitionAuthority(
            **{
                **pre.model_dump(),
                "completion_boundary_ref": "COMPLETE-WITHOUT-BEGIN",
            }
        )


def test_established_target_state_must_match_target_context() -> None:
    item, _, target_state = authority(
        StrategyGoverningTransitionState.POST_TRANSITION
    )

    with pytest.raises(ValidationError, match="target durable state"):
        StrategyGoverningTransitionAuthority(
            **{
                **item.model_dump(),
                "established_target_state": target_state.model_copy(
                    update={"config_version": "WRONG"}
                ),
            }
        )


def test_source_context_must_match_frozen_c16_authority() -> None:
    item, source_state, _ = authority(
        StrategyGoverningTransitionState.PRE_TRANSITION
    )

    changed = source_instance().model_copy(
        update={"strategy_version": "2.0.0"}
    )

    with pytest.raises(
        StrategyGoverningTransitionIntegrityError,
        match="C16 authority",
    ):
        evaluate_governing_transition(
            authority=item,
            source_instance=changed,
            durable_state=source_state,
        )


def test_restart_current_deployment_or_wall_clock_are_not_classification_inputs() -> None:
    item, _, _ = authority(
        StrategyGoverningTransitionState.TRANSITION_IN_PROGRESS
    )

    fields = type(item).model_fields
    assert "current_deployment" not in fields
    assert "latest_config" not in fields
    assert "restart_state" not in fields
    assert "wall_clock" not in fields
