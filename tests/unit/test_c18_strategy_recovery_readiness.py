from __future__ import annotations

import pytest

from persistence.recovery import (
    evaluate_authoritative_decision_cohort_trading_readiness,
    evaluate_authoritative_strategy_trading_readiness,
)
from strategy.instance import (
    CanonicalInstrumentBindingProvenance,
    StrategyInstance,
    config_fingerprint,
)
from strategy.recovery import (
    BrokerAccountExecutionReadyInput,
    CompletenessAuthorityClass,
    CompletenessEvidenceAuthority,
    CompletenessRequirementAuthority,
    CompletenessRequirementClassification,
    DecisionPolicyAuthorityClass,
    DecisionPolicyAuthorityRef,
    K520ApplicabilityClassification,
    K520ApplicabilityEvidence,
    RequiredCohortMembershipEvidence,
    StartupCatchUpOutputKind,
    StrategyAuthorityRef,
    StrategyDurableStateReference,
    StrategyGoverningContext,
    StrategyGoverningTransitionAuthority,
    StrategyGoverningTransitionPhaseEvidence,
    StrategyGoverningTransitionPhaseKind,
    StrategyGoverningTransitionResolution,
    StrategyGoverningTransitionResolutionKind,
    StrategyGoverningTransitionResolutionReceipt,
    StrategyRestoreValidEvidence,
    StrategyStateSchemaReference,
    evaluate_completeness_readiness_receipt,
    evaluate_generic_startup_catch_up_output,
    evaluate_k520_applicability_receipt,
)


MOR1 = "mor1_" + ("a" * 64)


def binding() -> CanonicalInstrumentBindingProvenance:
    return CanonicalInstrumentBindingProvenance(
        instrument_id=101,
        authority_id="CANONICAL-INSTRUMENT-PROVISIONING",
        authority_version="V1",
        reference_id="BIND-C18",
    )


def instance(strategy_instance_id: str = "SI-1") -> StrategyInstance:
    config = {"symbol": "TX", "timeframe": "1m"}
    return StrategyInstance(
        strategy_instance_id=strategy_instance_id,
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
    item: StrategyInstance,
    *,
    version: str = "C1",
    fingerprint: str | None = None,
    policy: str = "DP-1",
    schema: int = 1,
) -> StrategyGoverningContext:
    return StrategyGoverningContext(
        strategy_instance_id=item.strategy_instance_id,
        strategy_id=item.strategy_id,
        config_authority=StrategyAuthorityRef(
            authority_id="STRATEGY-CONFIG",
            authority_version=version,
        ),
        config_version=version,
        config_fingerprint=fingerprint or item.config_fingerprint,
        implementation_revision=item.implementation_revision,
        instrument_id=item.instrument_id,
        instrument_binding_provenance=item.instrument_binding_provenance,
        timeframe=item.timeframe,
        decision_policy_version=policy,
        state_schema_reference=StrategyStateSchemaReference(
            strategy_id=item.strategy_id,
            schema_version=schema,
        ),
    )


def descriptor(item: StrategyInstance) -> StrategyGoverningTransitionAuthority:
    target_fp = config_fingerprint(
        {"symbol": "TX", "timeframe": "1m", "mode": "target"}
    )
    return StrategyGoverningTransitionAuthority(
        transition_id=f"TR-{item.strategy_instance_id}",
        strategy_instance_id=item.strategy_instance_id,
        source_context=context(item),
        target_context=context(
            item,
            version="C2",
            fingerprint=target_fp,
            policy="DP-2",
            schema=2,
        ),
        compatibility_authority=StrategyAuthorityRef(
            authority_id="STRATEGY-COMPATIBILITY",
            authority_version="V1",
        ),
        transition_policy=StrategyAuthorityRef(
            authority_id="GOVERNING-TRANSITION",
            authority_version="V1",
        ),
    )


def transition_resolution(
    item: StrategyInstance,
    *,
    phase: str = "NO_ACTIVE",
    revision: int = 1,
) -> StrategyGoverningTransitionResolution:
    d = descriptor(item)

    if phase == "NO_ACTIVE":
        receipt = StrategyGoverningTransitionResolutionReceipt(
            resolution_id=f"RES-{item.strategy_instance_id}-{revision}",
            strategy_instance_id=item.strategy_instance_id,
            effective_governing_context=d.source_context,
            resolution_authority=StrategyAuthorityRef(
                authority_id="STRATEGY-GOVERNING-TRANSITION-RESOLUTION",
                authority_version="V1",
            ),
            resolution_kind=(
                StrategyGoverningTransitionResolutionKind.NO_ACTIVE_TRANSITION
            ),
            resolution_revision=revision,
            currentness_evidence_ref=f"HEAD-{revision}",
        )
        return StrategyGoverningTransitionResolution(
            receipt=receipt,
            current_head_revision=revision,
        )

    phases = ()
    effective = d.source_context

    begin = StrategyGoverningTransitionPhaseEvidence(
        evidence_id="BEGIN",
        transition_id=d.transition_id,
        strategy_instance_id=item.strategy_instance_id,
        kind=StrategyGoverningTransitionPhaseKind.BEGIN_EFFECTIVE,
        boundary_ref="BEGIN-1",
        evidence_authority=StrategyAuthorityRef(
            authority_id="TRANSITION-BOUNDARY",
            authority_version="V1",
        ),
    )

    if phase == "IN_PROGRESS":
        phases = (begin,)
    elif phase == "POST":
        target = d.target_context
        target_state = StrategyDurableStateReference(
            snapshot_id="TARGET",
            strategy_instance_id=target.strategy_instance_id,
            strategy_id=target.strategy_id,
            config_version=target.config_version,
            config_fingerprint=target.config_fingerprint,
            implementation_revision=target.implementation_revision,
            instrument_id=target.instrument_id,
            timeframe=target.timeframe,
            state_schema_reference=target.state_schema_reference,
        )
        completion = StrategyGoverningTransitionPhaseEvidence(
            evidence_id="COMPLETE",
            transition_id=d.transition_id,
            strategy_instance_id=item.strategy_instance_id,
            kind=StrategyGoverningTransitionPhaseKind.COMPLETION,
            boundary_ref="COMPLETE-1",
            evidence_authority=StrategyAuthorityRef(
                authority_id="TRANSITION-BOUNDARY",
                authority_version="V1",
            ),
            established_target_state=target_state,
        )
        phases = (begin, completion)
        effective = d.target_context
    elif phase != "PRE":
        raise ValueError(phase)

    receipt = StrategyGoverningTransitionResolutionReceipt(
        resolution_id=f"RES-{item.strategy_instance_id}-{revision}",
        strategy_instance_id=item.strategy_instance_id,
        effective_governing_context=effective,
        resolution_authority=StrategyAuthorityRef(
            authority_id="STRATEGY-GOVERNING-TRANSITION-RESOLUTION",
            authority_version="V1",
        ),
        resolution_kind=(
            StrategyGoverningTransitionResolutionKind.ACTIVE_TRANSITION
        ),
        transition_id=d.transition_id,
        resolution_revision=revision,
        currentness_evidence_ref=f"HEAD-{revision}",
    )
    return StrategyGoverningTransitionResolution(
        receipt=receipt,
        current_head_revision=revision,
        transition_authority=d,
        phase_evidence=phases,
    )


def k520_receipt(
    ctx: StrategyGoverningContext,
    claim: K520ApplicabilityClassification = (
        K520ApplicabilityClassification.NOT_APPLICABLE_PROVEN
    ),
):
    evidence = K520ApplicabilityEvidence(
        evidence_id=f"K520-{ctx.config_version}",
        strategy_instance_id=ctx.strategy_instance_id,
        strategy_id=ctx.strategy_id,
        config_version=ctx.config_version,
        config_fingerprint=ctx.config_fingerprint,
        implementation_revision=ctx.implementation_revision,
        instrument_id=ctx.instrument_id,
        instrument_binding_provenance=ctx.instrument_binding_provenance,
        timeframe=ctx.timeframe,
        feature_dependency_contract=StrategyAuthorityRef(
            authority_id="FEATURE-DEPENDENCY-CONTRACT",
            authority_version="V1",
        ),
        classification_claim=claim,
        required_replay_horizon=520,
        available_replay_horizon=520,
        governing_observation_frontier_revision_id=MOR1,
        evaluated_observation_frontier_revision_id=MOR1,
        current_observation_frontier_revision_id=MOR1,
        causal_frontier_ref="CAUSAL",
        currentness_evidence_ref="CURRENT",
        proof_authority=StrategyAuthorityRef(
            authority_id="K520-PROOF",
            authority_version="V1",
        ),
    )
    return evaluate_k520_applicability_receipt(
        governing_context=ctx,
        evidence=evidence,
    )


def completeness_receipt(
    ctx: StrategyGoverningContext,
    *,
    authority_class: CompletenessAuthorityClass = CompletenessAuthorityClass.PRODUCTION,
    consumer: str | None = None,
    scope: str | None = None,
    current_world: str = "WORLD-1",
):
    consumer = consumer or f"STRATEGY-INSTANCE:{ctx.strategy_instance_id}"
    scope = scope or f"INSTRUMENT:{ctx.instrument_id}/TIMEFRAME:{ctx.timeframe}"
    requirement = CompletenessRequirementAuthority(
        requirement_id="REQ",
        consumer_ref=consumer,
        scope_ref=scope,
        stream_ref="MARKET-OBSERVATION:PRIMARY",
        horizon_ref="HORIZON:RECOVERY-CUT",
        policy_authority=StrategyAuthorityRef(
            authority_id="COMPLETENESS-POLICY",
            authority_version="V1",
        ),
        authority_class=authority_class,
        classification=CompletenessRequirementClassification.REQUIRED,
    )
    evidence = CompletenessEvidenceAuthority(
        evidence_id="COMPLETE",
        consumer_ref=consumer,
        scope_ref=scope,
        stream_ref=requirement.stream_ref,
        horizon_ref=requirement.horizon_ref,
        policy_authority=requirement.policy_authority,
        authority_class=authority_class,
        evaluated_world_ref="WORLD-1",
        current_world_ref=current_world,
        evaluated_frontier_revision_id=MOR1,
        current_frontier_revision_id=MOR1,
        currentness_evidence_ref="CURRENTNESS-1",
        evidence_authority=StrategyAuthorityRef(
            authority_id="COMPLETENESS-EVIDENCE",
            authority_version="V1",
        ),
        complete=True,
    )
    return evaluate_completeness_readiness_receipt(
        governing_context=ctx,
        requirement=requirement,
        evidence=evidence,
        runtime_authority_class=authority_class,
    )


def restore(ctx: StrategyGoverningContext, valid: bool = True):
    return StrategyRestoreValidEvidence(
        evidence_id="RESTORE",
        strategy_instance_id=ctx.strategy_instance_id,
        governing_context=ctx,
        restore_authority_ref="RESTORE-AUTH",
        valid=valid,
    )


class TransitionRepo:
    def __init__(self, value):
        self.value = value

    def current_resolution(self, strategy_instance_id):
        return self.value


def strategy_ready(
    item: StrategyInstance,
    *,
    resolution=None,
    c19=None,
    c20=None,
    restore_context=None,
    broker_ready=True,
    restore_valid=True,
    runtime_class=CompletenessAuthorityClass.PRODUCTION,
):
    resolution = (
        resolution
        if resolution is not None
        else transition_resolution(item)
    )
    ctx = resolution.receipt.effective_governing_context
    c19 = c19 if c19 is not None else k520_receipt(ctx)
    c20 = c20 if c20 is not None else completeness_receipt(ctx)
    return evaluate_authoritative_strategy_trading_readiness(
        transition_repository=TransitionRepo(resolution),
        instance=item,
        broker_account=BrokerAccountExecutionReadyInput(
            authority_ref="W4R-D:C15:ACCOUNT-READY",
            ready=broker_ready,
        ),
        restore=restore(restore_context or ctx, valid=restore_valid),
        k520_receipt=c19,
        k520_evidence=None,
        completeness_receipt=c20,
        runtime_completeness_authority_class=runtime_class,
    )


def policy(
    authority_class=DecisionPolicyAuthorityClass.PRODUCTION,
    version="DP-1",
):
    return DecisionPolicyAuthorityRef(
        policy_id="DECISION-POLICY",
        policy_version=version,
        authority=StrategyAuthorityRef(
            authority_id="DECISION-DOMAIN",
            authority_version="V1",
        ),
        authority_class=authority_class,
    )


def membership(
    required,
    *,
    stale_policy=False,
    stale_membership=False,
    policy_value=None,
):
    return RequiredCohortMembershipEvidence(
        evidence_id="MEMBERSHIP",
        cohort_id="COHORT-1",
        policy=policy_value or policy(),
        required_strategy_instance_ids=required,
        membership_authority=StrategyAuthorityRef(
            authority_id="DECISION-COHORT-MEMBERSHIP",
            authority_version="V1",
        ),
        evaluated_policy_currentness_ref="POLICY-R1",
        current_policy_currentness_ref=(
            "POLICY-R2" if stale_policy else "POLICY-R1"
        ),
        evaluated_membership_currentness_ref="MEMBER-R1",
        current_membership_currentness_ref=(
            "MEMBER-R2" if stale_membership else "MEMBER-R1"
        ),
    )


class CohortProvider:
    def __init__(self, value):
        self.value = value

    def resolve_required_membership(self, *, cohort_id, policy):
        return self.value


def test_ce10_missing_transition_resolver_or_resolution_fails_closed():
    item = instance()
    ctx = context(item)
    kwargs = dict(
        instance=item,
        broker_account=BrokerAccountExecutionReadyInput(
            authority_ref="ACCOUNT",
            ready=True,
        ),
        restore=restore(ctx),
        k520_receipt=k520_receipt(ctx),
        k520_evidence=None,
        completeness_receipt=completeness_receipt(ctx),
        runtime_completeness_authority_class=CompletenessAuthorityClass.PRODUCTION,
    )
    result = evaluate_authoritative_strategy_trading_readiness(
        transition_repository=None,
        **kwargs,
    )
    assert result.strategy_trading_ready is False
    assert any("resolution" in reason for reason in result.reasons)

    result = evaluate_authoritative_strategy_trading_readiness(
        transition_repository=TransitionRepo(None),
        **kwargs,
    )
    assert result.strategy_trading_ready is False


def test_positive_current_no_active_transition_can_satisfy_transition_gate():
    assert strategy_ready(instance()).strategy_trading_ready is True


def test_transition_in_progress_is_not_ready():
    item = instance()
    res = transition_resolution(item, phase="IN_PROGRESS")
    result = strategy_ready(item, resolution=res)
    assert result.strategy_trading_ready is False
    assert any("in progress" in reason for reason in result.reasons)


def test_ce06_post_target_c2_rejects_c19_receipt_from_source_c1():
    item = instance()
    res = transition_resolution(item, phase="POST")
    target = res.receipt.effective_governing_context
    source = res.transition_authority.source_context
    result = strategy_ready(
        item,
        resolution=res,
        restore_context=target,
        c19=k520_receipt(source),
        c20=completeness_receipt(target),
    )
    assert result.strategy_trading_ready is False
    assert any("C19 receipt" in reason for reason in result.reasons)


def test_ce07_exact_post_c2_c19_receipt_can_be_consumed():
    item = instance()
    res = transition_resolution(item, phase="POST")
    target = res.receipt.effective_governing_context
    result = strategy_ready(
        item,
        resolution=res,
        restore_context=target,
        c19=k520_receipt(target),
        c20=completeness_receipt(target),
    )
    assert result.strategy_trading_ready is True


@pytest.mark.parametrize(
    "authority_class",
    (CompletenessAuthorityClass.TEST, CompletenessAuthorityClass.SANDBOX),
)
def test_ce08_production_strategy_rejects_nonproduction_c20_ready(authority_class):
    item = instance()
    ctx = context(item)
    result = strategy_ready(
        item,
        c20=completeness_receipt(ctx, authority_class=authority_class),
        runtime_class=CompletenessAuthorityClass.PRODUCTION,
    )
    assert result.strategy_trading_ready is False


def test_ce09_wrong_c20_consumer_scope_or_world_cannot_satisfy_strategy():
    item = instance()
    ctx = context(item)
    wrong_scope = completeness_receipt(
        ctx,
        consumer="STRATEGY-INSTANCE:OTHER",
        scope="INSTRUMENT:999/TIMEFRAME:1m",
    )
    result = strategy_ready(item, c20=wrong_scope)
    assert result.strategy_trading_ready is False
    assert any("consumer/scope" in reason for reason in result.reasons)

    stale = completeness_receipt(ctx, current_world="WORLD-2")
    result = strategy_ready(item, c20=stale)
    assert result.strategy_trading_ready is False


def test_broker_ready_does_not_imply_strategy_ready_when_restore_invalid():
    result = strategy_ready(instance(), restore_valid=False)
    assert result.broker_account_execution_ready is True
    assert result.strategy_restore_valid is False
    assert result.strategy_trading_ready is False


def test_c19_required_without_approved_k520_evidence_is_not_ready():
    item = instance()
    res = transition_resolution(item)
    ctx = res.receipt.effective_governing_context
    result = strategy_ready(
        item,
        resolution=res,
        c19=k520_receipt(ctx, K520ApplicabilityClassification.REQUIRED),
    )
    assert result.strategy_trading_ready is False
    assert any("required K520 recovery evidence" in x for x in result.reasons)


def test_ce13_authoritative_provider_cannot_be_shrunk_by_caller_readiness():
    si1 = instance("SI-1")
    authoritative = membership(("SI-1", "SI-2"))
    result = evaluate_authoritative_decision_cohort_trading_readiness(
        provider=CohortProvider(authoritative),
        cohort_id="COHORT-1",
        governing_policy=policy(),
        strategy_readiness=(strategy_ready(si1),),
        runtime_authority_class=DecisionPolicyAuthorityClass.PRODUCTION,
    )
    assert result.decision_cohort_trading_ready is False
    assert result.missing_strategy_instance_ids == ("SI-2",)


@pytest.mark.parametrize("which", ("policy", "membership"))
def test_ce14_ce15_stale_authoritative_membership_is_not_ready(which):
    si1 = instance("SI-1")
    authoritative = membership(
        ("SI-1",),
        stale_policy=(which == "policy"),
        stale_membership=(which == "membership"),
    )
    result = evaluate_authoritative_decision_cohort_trading_readiness(
        provider=CohortProvider(authoritative),
        cohort_id="COHORT-1",
        governing_policy=policy(),
        strategy_readiness=(strategy_ready(si1),),
        runtime_authority_class=DecisionPolicyAuthorityClass.PRODUCTION,
    )
    assert result.decision_cohort_trading_ready is False


def test_stale_decision_policy_version_is_not_ready():
    si1 = instance("SI-1")
    authoritative = membership(
        ("SI-1",),
        policy_value=policy(version="DP-OLD"),
    )
    result = evaluate_authoritative_decision_cohort_trading_readiness(
        provider=CohortProvider(authoritative),
        cohort_id="COHORT-1",
        governing_policy=policy(),
        strategy_readiness=(strategy_ready(si1),),
        runtime_authority_class=DecisionPolicyAuthorityClass.PRODUCTION,
    )
    assert result.decision_cohort_trading_ready is False


def test_ce16_provider_unavailable_is_not_cohort_ready():
    result = evaluate_authoritative_decision_cohort_trading_readiness(
        provider=None,
        cohort_id="COHORT-1",
        governing_policy=policy(),
        strategy_readiness=(strategy_ready(instance()),),
        runtime_authority_class=DecisionPolicyAuthorityClass.PRODUCTION,
    )
    assert result.decision_cohort_trading_ready is False


def test_complete_authoritative_cohort_can_be_ready():
    si1 = instance("SI-1")
    si2 = instance("SI-2")
    authoritative = membership(("SI-1", "SI-2"))
    result = evaluate_authoritative_decision_cohort_trading_readiness(
        provider=CohortProvider(authoritative),
        cohort_id="COHORT-1",
        governing_policy=policy(),
        strategy_readiness=(strategy_ready(si1), strategy_ready(si2)),
        runtime_authority_class=DecisionPolicyAuthorityClass.PRODUCTION,
    )
    assert result.decision_cohort_trading_ready is True


@pytest.mark.parametrize("output_kind", tuple(StartupCatchUpOutputKind))
def test_generic_startup_catch_up_remains_recovery_isolated(output_kind):
    result = evaluate_generic_startup_catch_up_output(
        output_kind=output_kind,
        action_label="PROTECTIVE",
    )
    assert result.recovery_isolated is True
    assert result.normal_material_action_allowed is False
    assert result.historical_signal_promotable is False
