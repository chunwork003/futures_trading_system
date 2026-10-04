from __future__ import annotations

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
    evaluate_k520_applicability_receipt,
)
from strategy.registry import StrategyRegistry


MOR1 = "mor1_" + ("a" * 64)


def instance():
    config = {"symbol": "TX", "timeframe": "1m"}
    provenance = CanonicalInstrumentBindingProvenance(
        instrument_id=101,
        authority_id="CANONICAL-INSTRUMENT-PROVISIONING",
        authority_version="V1",
        reference_id="BIND-P7-RF01",
    )
    return StrategyInstance(
        strategy_instance_id="SI-P7-RF01",
        strategy_id="EMA_CROSS",
        strategy_version="1.0.0",
        config_version="C1",
        config_fingerprint=config_fingerprint(config),
        instrument_id=101,
        timeframe="1m",
        config_json=config,
        instrument_binding_provenance=provenance,
    )


def context(si, version="C1", fingerprint=None, policy="DP-1", schema=1):
    return StrategyGoverningContext(
        strategy_instance_id=si.strategy_instance_id,
        strategy_id=si.strategy_id,
        config_authority=StrategyAuthorityRef(
            authority_id="STRATEGY-CONFIG",
            authority_version=version,
        ),
        config_version=version,
        config_fingerprint=fingerprint or si.config_fingerprint,
        implementation_revision=si.implementation_revision,
        instrument_id=si.instrument_id,
        instrument_binding_provenance=si.instrument_binding_provenance,
        timeframe=si.timeframe,
        decision_policy_version=policy,
        state_schema_reference=StrategyStateSchemaReference(
            strategy_id=si.strategy_id,
            schema_version=schema,
        ),
    )


def k520(ctx):
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
            authority_id="FEATURE-CONTRACT",
            authority_version="V1",
        ),
        classification_claim=K520ApplicabilityClassification.NOT_APPLICABLE_PROVEN,
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


def completeness(ctx):
    consumer = f"STRATEGY-INSTANCE:{ctx.strategy_instance_id}"
    scope = f"INSTRUMENT:{ctx.instrument_id}/TIMEFRAME:{ctx.timeframe}"
    requirement = CompletenessRequirementAuthority(
        requirement_id="REQ",
        consumer_ref=consumer,
        scope_ref=scope,
        stream_ref="MARKET-OBSERVATION:PRIMARY",
        horizon_ref="HORIZON:RECOVERY-CUT",
        policy_authority=StrategyAuthorityRef(
            authority_id="COMPLETE-POLICY",
            authority_version="V1",
        ),
        authority_class=CompletenessAuthorityClass.PRODUCTION,
        classification=CompletenessRequirementClassification.REQUIRED,
    )
    evidence = CompletenessEvidenceAuthority(
        evidence_id="COMPLETE",
        consumer_ref=consumer,
        scope_ref=scope,
        stream_ref=requirement.stream_ref,
        horizon_ref=requirement.horizon_ref,
        policy_authority=requirement.policy_authority,
        authority_class=CompletenessAuthorityClass.PRODUCTION,
        evaluated_world_ref="WORLD",
        current_world_ref="WORLD",
        evaluated_frontier_revision_id=MOR1,
        current_frontier_revision_id=MOR1,
        currentness_evidence_ref="CURRENT",
        evidence_authority=StrategyAuthorityRef(
            authority_id="COMPLETE-EVIDENCE",
            authority_version="V1",
        ),
        complete=True,
    )
    return evaluate_completeness_readiness_receipt(
        governing_context=ctx,
        requirement=requirement,
        evidence=evidence,
        runtime_authority_class=CompletenessAuthorityClass.PRODUCTION,
    )


class TransitionRepo:
    def __init__(self, value):
        self.value = value

    def current_resolution(self, strategy_instance_id):
        return self.value


class CohortProvider:
    def __init__(self, value):
        self.value = value

    def resolve_required_membership(self, *, cohort_id, policy):
        return self.value


def positive_no_active(si, ctx):
    receipt = StrategyGoverningTransitionResolutionReceipt(
        resolution_id="RES-NONE",
        strategy_instance_id=si.strategy_instance_id,
        effective_governing_context=ctx,
        resolution_authority=StrategyAuthorityRef(
            authority_id="STRATEGY-GOVERNING-TRANSITION-RESOLUTION",
            authority_version="V1",
        ),
        resolution_kind=StrategyGoverningTransitionResolutionKind.NO_ACTIVE_TRANSITION,
        resolution_revision=1,
        currentness_evidence_ref="HEAD-1",
    )
    return StrategyGoverningTransitionResolution(
        receipt=receipt,
        current_head_revision=1,
    )


def test_rf01_integrated_positive_authority_chain_c16_to_cohort():
    si = instance()
    registry = StrategyRegistry()
    registry.register(
        si.strategy_id,
        si.implementation_revision,
        lambda **kwargs: kwargs,
    )
    assert registry.validate_governing_instance(si).version == si.implementation_revision

    ctx = context(si)
    resolution = positive_no_active(si, ctx)
    strategy_result = evaluate_authoritative_strategy_trading_readiness(
        transition_repository=TransitionRepo(resolution),
        instance=si,
        broker_account=BrokerAccountExecutionReadyInput(
            authority_ref="ACCOUNT",
            ready=True,
        ),
        restore=StrategyRestoreValidEvidence(
            evidence_id="RESTORE",
            strategy_instance_id=si.strategy_instance_id,
            governing_context=ctx,
            restore_authority_ref="RESTORE-AUTH",
            valid=True,
        ),
        k520_receipt=k520(ctx),
        k520_evidence=None,
        completeness_receipt=completeness(ctx),
        runtime_completeness_authority_class=CompletenessAuthorityClass.PRODUCTION,
    )
    assert strategy_result.strategy_trading_ready is True

    policy = DecisionPolicyAuthorityRef(
        policy_id="DECISION-POLICY",
        policy_version="DP-1",
        authority=StrategyAuthorityRef(
            authority_id="DECISION-DOMAIN",
            authority_version="V1",
        ),
        authority_class=DecisionPolicyAuthorityClass.PRODUCTION,
    )
    membership = RequiredCohortMembershipEvidence(
        evidence_id="MEMBERSHIP",
        cohort_id="COHORT",
        policy=policy,
        required_strategy_instance_ids=(si.strategy_instance_id,),
        membership_authority=StrategyAuthorityRef(
            authority_id="COHORT-MEMBERSHIP",
            authority_version="V1",
        ),
        evaluated_policy_currentness_ref="P1",
        current_policy_currentness_ref="P1",
        evaluated_membership_currentness_ref="M1",
        current_membership_currentness_ref="M1",
    )
    cohort = evaluate_authoritative_decision_cohort_trading_readiness(
        provider=CohortProvider(membership),
        cohort_id="COHORT",
        governing_policy=policy,
        strategy_readiness=(strategy_result,),
        runtime_authority_class=DecisionPolicyAuthorityClass.PRODUCTION,
    )
    assert cohort.decision_cohort_trading_ready is True


def test_rf01_post_transition_rejects_old_c19_world():
    si = instance()
    source = context(si)
    target = context(
        si,
        version="C2",
        fingerprint=config_fingerprint(
            {"symbol": "TX", "timeframe": "1m", "mode": "target"}
        ),
        policy="DP-2",
        schema=2,
    )
    descriptor = StrategyGoverningTransitionAuthority(
        transition_id="TR",
        strategy_instance_id=si.strategy_instance_id,
        source_context=source,
        target_context=target,
        compatibility_authority=StrategyAuthorityRef(
            authority_id="COMPAT",
            authority_version="V1",
        ),
        transition_policy=StrategyAuthorityRef(
            authority_id="TRANSITION",
            authority_version="V1",
        ),
    )
    begin = StrategyGoverningTransitionPhaseEvidence(
        evidence_id="BEGIN",
        transition_id="TR",
        strategy_instance_id=si.strategy_instance_id,
        kind=StrategyGoverningTransitionPhaseKind.BEGIN_EFFECTIVE,
        boundary_ref="B",
        evidence_authority=StrategyAuthorityRef(
            authority_id="BOUNDARY",
            authority_version="V1",
        ),
    )
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
    complete = StrategyGoverningTransitionPhaseEvidence(
        evidence_id="COMPLETE",
        transition_id="TR",
        strategy_instance_id=si.strategy_instance_id,
        kind=StrategyGoverningTransitionPhaseKind.COMPLETION,
        boundary_ref="C",
        evidence_authority=StrategyAuthorityRef(
            authority_id="BOUNDARY",
            authority_version="V1",
        ),
        established_target_state=target_state,
    )
    receipt = StrategyGoverningTransitionResolutionReceipt(
        resolution_id="RES-POST",
        strategy_instance_id=si.strategy_instance_id,
        effective_governing_context=target,
        resolution_authority=StrategyAuthorityRef(
            authority_id="STRATEGY-GOVERNING-TRANSITION-RESOLUTION",
            authority_version="V1",
        ),
        resolution_kind=StrategyGoverningTransitionResolutionKind.ACTIVE_TRANSITION,
        transition_id="TR",
        resolution_revision=1,
        currentness_evidence_ref="HEAD-1",
    )
    resolution = StrategyGoverningTransitionResolution(
        receipt=receipt,
        current_head_revision=1,
        transition_authority=descriptor,
        phase_evidence=(begin, complete),
    )
    result = evaluate_authoritative_strategy_trading_readiness(
        transition_repository=TransitionRepo(resolution),
        instance=si,
        broker_account=BrokerAccountExecutionReadyInput(
            authority_ref="ACCOUNT",
            ready=True,
        ),
        restore=StrategyRestoreValidEvidence(
            evidence_id="RESTORE",
            strategy_instance_id=si.strategy_instance_id,
            governing_context=target,
            restore_authority_ref="RESTORE-AUTH",
            valid=True,
        ),
        k520_receipt=k520(source),
        k520_evidence=None,
        completeness_receipt=completeness(target),
        runtime_completeness_authority_class=CompletenessAuthorityClass.PRODUCTION,
    )
    assert result.strategy_trading_ready is False
    assert any("C19 receipt" in reason for reason in result.reasons)
