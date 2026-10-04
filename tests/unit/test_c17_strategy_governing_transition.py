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
    StrategyGoverningTransitionPhaseEvidence,
    StrategyGoverningTransitionPhaseKind,
    StrategyGoverningTransitionResolution,
    StrategyGoverningTransitionResolutionKind,
    StrategyGoverningTransitionResolutionReceipt,
    StrategyGoverningTransitionState,
    StrategyStateSchemaReference,
    classify_governing_transition,
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


def context(version: str, fingerprint: str, policy: str, schema: int):
    return StrategyGoverningContext(
        strategy_instance_id="SI-C17",
        strategy_id="EMA_CROSS",
        config_authority=StrategyAuthorityRef(
            authority_id="STRATEGY-CONFIG",
            authority_version=version,
        ),
        config_version=version,
        config_fingerprint=fingerprint,
        implementation_revision="1.0.0",
        instrument_id=101,
        instrument_binding_provenance=binding(),
        timeframe="1m",
        decision_policy_version=policy,
        state_schema_reference=StrategyStateSchemaReference(
            strategy_id="EMA_CROSS",
            schema_version=schema,
        ),
    )


def descriptor():
    item = source_instance()
    target_fp = config_fingerprint(
        {"symbol": "TX", "timeframe": "1m", "mode": "target"}
    )
    return StrategyGoverningTransitionAuthority(
        transition_id="TR-C17",
        strategy_instance_id=item.strategy_instance_id,
        source_context=context("C1", item.config_fingerprint, "DP-1", 1),
        target_context=context("C2", target_fp, "DP-2", 2),
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


def state(ctx: StrategyGoverningContext, snapshot_id: str):
    return StrategyDurableStateReference(
        snapshot_id=snapshot_id,
        strategy_instance_id=ctx.strategy_instance_id,
        strategy_id=ctx.strategy_id,
        config_version=ctx.config_version,
        config_fingerprint=ctx.config_fingerprint,
        implementation_revision=ctx.implementation_revision,
        instrument_id=ctx.instrument_id,
        timeframe=ctx.timeframe,
        state_schema_reference=ctx.state_schema_reference,
    )


def begin(item=None, *, evidence_id="EV-BEGIN", boundary="BEGIN-1"):
    item = item or descriptor()
    return StrategyGoverningTransitionPhaseEvidence(
        evidence_id=evidence_id,
        transition_id=item.transition_id,
        strategy_instance_id=item.strategy_instance_id,
        kind=StrategyGoverningTransitionPhaseKind.BEGIN_EFFECTIVE,
        boundary_ref=boundary,
        evidence_authority=StrategyAuthorityRef(
            authority_id="TRANSITION-BOUNDARY",
            authority_version="V1",
        ),
    )


def completion(item=None, *, evidence_id="EV-COMPLETE", boundary="COMPLETE-1"):
    item = item or descriptor()
    return StrategyGoverningTransitionPhaseEvidence(
        evidence_id=evidence_id,
        transition_id=item.transition_id,
        strategy_instance_id=item.strategy_instance_id,
        kind=StrategyGoverningTransitionPhaseKind.COMPLETION,
        boundary_ref=boundary,
        evidence_authority=StrategyAuthorityRef(
            authority_id="TRANSITION-BOUNDARY",
            authority_version="V1",
        ),
        established_target_state=state(item.target_context, "SS-TARGET"),
    )


def receipt(item, kind, revision=1, *, effective=None):
    return StrategyGoverningTransitionResolutionReceipt(
        resolution_id=f"RES-{revision}",
        strategy_instance_id=item.strategy_instance_id,
        effective_governing_context=effective or item.source_context,
        resolution_authority=StrategyAuthorityRef(
            authority_id="STRATEGY-GOVERNING-TRANSITION-RESOLUTION",
            authority_version="V1",
        ),
        resolution_kind=kind,
        transition_id=(
            item.transition_id
            if kind is StrategyGoverningTransitionResolutionKind.ACTIVE_TRANSITION
            else None
        ),
        resolution_revision=revision,
        currentness_evidence_ref=f"HEAD-{revision}",
    )


def test_c17_has_exactly_three_states_and_descriptor_has_no_phase_material():
    assert tuple(x.value for x in StrategyGoverningTransitionState) == (
        "PRE_TRANSITION",
        "TRANSITION_IN_PROGRESS",
        "POST_TRANSITION",
    )
    for field in (
        "begin_effective_boundary_ref",
        "completion_boundary_ref",
        "established_target_state",
    ):
        assert field not in StrategyGoverningTransitionAuthority.model_fields


def test_ce01_same_transition_identity_progresses_pre_in_progress_post():
    item = descriptor()
    assert classify_governing_transition(
        authority=item
    ) is StrategyGoverningTransitionState.PRE_TRANSITION
    assert classify_governing_transition(
        authority=item,
        phase_evidence=(begin(item),),
    ) is StrategyGoverningTransitionState.TRANSITION_IN_PROGRESS
    assert classify_governing_transition(
        authority=item,
        phase_evidence=(begin(item), completion(item)),
    ) is StrategyGoverningTransitionState.POST_TRANSITION
    assert item.transition_id == "TR-C17"


def test_ce02_descriptor_is_immutable_and_conflicting_identity_material_is_distinct():
    item = descriptor()
    with pytest.raises(ValidationError):
        item.transition_id = "OTHER"
    changed = item.model_copy(
        update={"target_context": item.source_context}
    )
    assert changed != item


def test_ce03_conflicting_second_begin_fails_closed():
    item = descriptor()
    with pytest.raises(
        StrategyGoverningTransitionIntegrityError,
        match="conflicting BEGIN",
    ):
        classify_governing_transition(
            authority=item,
            phase_evidence=(
                begin(item),
                begin(item, evidence_id="EV-BEGIN-2", boundary="BEGIN-OTHER"),
            ),
        )


def test_ce04_completion_without_begin_fails_closed():
    item = descriptor()
    with pytest.raises(
        StrategyGoverningTransitionIntegrityError,
        match="without BEGIN",
    ):
        classify_governing_transition(
            authority=item,
            phase_evidence=(completion(item),),
        )


def test_ce05_conflicting_second_completion_fails_closed():
    item = descriptor()
    with pytest.raises(
        StrategyGoverningTransitionIntegrityError,
        match="conflicting COMPLETION",
    ):
        classify_governing_transition(
            authority=item,
            phase_evidence=(
                begin(item),
                completion(item),
                completion(
                    item,
                    evidence_id="EV-COMPLETE-2",
                    boundary="COMPLETE-OTHER",
                ),
            ),
        )


def test_post_requires_exact_target_durable_state():
    item = descriptor()
    target = state(item.target_context, "SS-TARGET")
    assert evaluate_governing_transition(
        authority=item,
        source_instance=source_instance(),
        durable_state=target,
        phase_evidence=(begin(item), completion(item)),
    ) is StrategyGoverningTransitionState.POST_TRANSITION

    with pytest.raises(
        StrategyGoverningTransitionIntegrityError,
        match="target-compatible",
    ):
        evaluate_governing_transition(
            authority=item,
            source_instance=source_instance(),
            durable_state=target.model_copy(update={"snapshot_id": "OTHER"}),
            phase_evidence=(begin(item), completion(item)),
        )


def test_source_context_must_match_frozen_c16_authority():
    item = descriptor()
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
            durable_state=state(item.source_context, "SS-SOURCE"),
        )


def test_ce11_positive_no_active_transition_is_not_fourth_state():
    item = descriptor()
    no_active = receipt(
        item,
        StrategyGoverningTransitionResolutionKind.NO_ACTIVE_TRANSITION,
    )
    resolved = StrategyGoverningTransitionResolution(
        receipt=no_active,
        current_head_revision=1,
    )
    assert resolved.transition_state is None
    assert len(tuple(StrategyGoverningTransitionState)) == 3


def test_ce12_stale_no_active_receipt_fails_closed():
    item = descriptor()
    no_active = receipt(
        item,
        StrategyGoverningTransitionResolutionKind.NO_ACTIVE_TRANSITION,
    )
    with pytest.raises(ValidationError, match="stale"):
        StrategyGoverningTransitionResolution(
            receipt=no_active,
            current_head_revision=2,
        )


def test_active_resolution_effective_context_must_match_derived_phase():
    item = descriptor()
    active = receipt(
        item,
        StrategyGoverningTransitionResolutionKind.ACTIVE_TRANSITION,
    )
    resolved = StrategyGoverningTransitionResolution(
        receipt=active,
        current_head_revision=1,
        transition_authority=item,
    )
    assert resolved.transition_state is StrategyGoverningTransitionState.PRE_TRANSITION

    wrong = receipt(
        item,
        StrategyGoverningTransitionResolutionKind.ACTIVE_TRANSITION,
        effective=item.target_context,
    )
    with pytest.raises(ValidationError, match="effective governing context"):
        StrategyGoverningTransitionResolution(
            receipt=wrong,
            current_head_revision=1,
            transition_authority=item,
        )
