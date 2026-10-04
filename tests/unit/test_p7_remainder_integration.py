from __future__ import annotations

import pytest

from strategy.instance import (
    CanonicalInstrumentBindingProvenance,
    StrategyInstance,
    config_fingerprint,
)
from strategy.recovery import (
    BrokerAccountExecutionReadyInput,
    CompletenessAuthorityClass,
    CompletenessEvidenceAuthority,
    CompletenessReadiness,
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
    StrategyGoverningTransitionState,
    StrategyRestoreValidEvidence,
    StrategyStateSchemaReference,
    evaluate_completeness_readiness,
    evaluate_decision_cohort_trading_readiness,
    evaluate_generic_startup_catch_up_output,
    evaluate_governing_transition,
    evaluate_k520_applicability,
    evaluate_strategy_trading_readiness,
)
from strategy.registry import StrategyRegistry


MOR1_A = "mor1_" + ("a" * 64)


def governing_instance() -> StrategyInstance:
    config = {
        "symbol": "TX",
        "timeframe": "1m",
    }
    return StrategyInstance(
        strategy_instance_id="SI-P7-INTEGRATION",
        strategy_id="EMA_CROSS",
        strategy_version="1.0.0",
        config_version="C1",
        config_fingerprint=config_fingerprint(config),
        instrument_id=101,
        timeframe="1m",
        config_json=config,
        instrument_binding_provenance=(
            CanonicalInstrumentBindingProvenance(
                instrument_id=101,
                authority_id="CANONICAL-INSTRUMENT-PROVISIONING",
                authority_version="V1",
                reference_id="BIND-P7-INTEGRATION",
            )
        ),
    )


def source_context(
    item: StrategyInstance,
) -> StrategyGoverningContext:
    return StrategyGoverningContext(
        strategy_instance_id=item.strategy_instance_id,
        strategy_id=item.strategy_id,
        config_authority=StrategyAuthorityRef(
            authority_id="STRATEGY-CONFIG",
            authority_version="C1",
        ),
        config_version=item.config_version,
        config_fingerprint=item.config_fingerprint,
        implementation_revision=item.implementation_revision,
        instrument_id=item.instrument_id,
        instrument_binding_provenance=(
            item.instrument_binding_provenance
        ),
        timeframe=item.timeframe,
        decision_policy_version="DP-1",
        state_schema_reference=StrategyStateSchemaReference(
            strategy_id=item.strategy_id,
            schema_version=1,
        ),
    )


def target_context(
    item: StrategyInstance,
) -> StrategyGoverningContext:
    target_config = {
        "symbol": "TX",
        "timeframe": "1m",
        "mode": "target",
    }
    return StrategyGoverningContext(
        strategy_instance_id=item.strategy_instance_id,
        strategy_id=item.strategy_id,
        config_authority=StrategyAuthorityRef(
            authority_id="STRATEGY-CONFIG",
            authority_version="C2",
        ),
        config_version="C2",
        config_fingerprint=config_fingerprint(target_config),
        implementation_revision=item.implementation_revision,
        instrument_id=item.instrument_id,
        instrument_binding_provenance=(
            item.instrument_binding_provenance
        ),
        timeframe=item.timeframe,
        decision_policy_version="DP-2",
        state_schema_reference=StrategyStateSchemaReference(
            strategy_id=item.strategy_id,
            schema_version=2,
        ),
    )


def source_state(
    item: StrategyInstance,
) -> StrategyDurableStateReference:
    return StrategyDurableStateReference(
        snapshot_id="SS-P7-SOURCE",
        strategy_instance_id=item.strategy_instance_id,
        strategy_id=item.strategy_id,
        config_version=item.config_version,
        config_fingerprint=item.config_fingerprint,
        implementation_revision=item.implementation_revision,
        instrument_id=item.instrument_id,
        timeframe=item.timeframe,
        state_schema_reference=StrategyStateSchemaReference(
            strategy_id=item.strategy_id,
            schema_version=1,
        ),
    )


def transition_authority(
    item: StrategyInstance,
    *,
    in_progress: bool = False,
) -> StrategyGoverningTransitionAuthority:
    values = dict(
        transition_id="TR-P7-INTEGRATION",
        strategy_instance_id=item.strategy_instance_id,
        source_context=source_context(item),
        target_context=target_context(item),
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
    if in_progress:
        values["begin_effective_boundary_ref"] = "BEGIN-P7-INTEGRATION"

    return StrategyGoverningTransitionAuthority(**values)


def k520_applicability(
    item: StrategyInstance,
) -> K520ApplicabilityClassification:
    evidence = K520ApplicabilityEvidence(
        evidence_id="K520-P7-INTEGRATION",
        strategy_instance_id=item.strategy_instance_id,
        strategy_id=item.strategy_id,
        config_version=item.config_version,
        config_fingerprint=item.config_fingerprint,
        implementation_revision=item.implementation_revision,
        instrument_id=item.instrument_id,
        instrument_binding_provenance=(
            item.instrument_binding_provenance
        ),
        timeframe=item.timeframe,
        feature_dependency_contract=StrategyAuthorityRef(
            authority_id="FEATURE-DEPENDENCY-CONTRACT",
            authority_version="V1",
        ),
        classification_claim=(
            K520ApplicabilityClassification.NOT_APPLICABLE_PROVEN
        ),
        required_replay_horizon=520,
        available_replay_horizon=520,
        governing_observation_frontier_revision_id=MOR1_A,
        evaluated_observation_frontier_revision_id=MOR1_A,
        current_observation_frontier_revision_id=MOR1_A,
        causal_frontier_ref="CAUSAL-P7-INTEGRATION",
        currentness_evidence_ref="CURRENT-P7-INTEGRATION",
        proof_authority=StrategyAuthorityRef(
            authority_id="K520-APPLICABILITY-PROOF",
            authority_version="V1",
        ),
    )
    return evaluate_k520_applicability(
        instance=item,
        evidence=evidence,
    )


def completeness_ready() -> CompletenessReadiness:
    requirement = CompletenessRequirementAuthority(
        requirement_id="COMPLETE-REQ-P7",
        consumer_ref="STRATEGY-INSTANCE:SI-P7-INTEGRATION",
        scope_ref="INSTRUMENT:101/TIMEFRAME:1m",
        stream_ref="MARKET-OBSERVATION:PRIMARY",
        horizon_ref="HORIZON:RECOVERY-CUT",
        policy_authority=StrategyAuthorityRef(
            authority_id="COMPLETENESS-REQUIREMENT-POLICY",
            authority_version="V1",
        ),
        authority_class=CompletenessAuthorityClass.PRODUCTION,
        classification=CompletenessRequirementClassification.REQUIRED,
    )
    evidence = CompletenessEvidenceAuthority(
        evidence_id="COMPLETE-EVIDENCE-P7",
        consumer_ref=requirement.consumer_ref,
        scope_ref=requirement.scope_ref,
        stream_ref=requirement.stream_ref,
        horizon_ref=requirement.horizon_ref,
        policy_authority=requirement.policy_authority,
        authority_class=CompletenessAuthorityClass.PRODUCTION,
        evaluated_world_ref="WORLD:P7-INTEGRATION",
        current_world_ref="WORLD:P7-INTEGRATION",
        evaluated_frontier_revision_id=MOR1_A,
        current_frontier_revision_id=MOR1_A,
        currentness_evidence_ref="CURRENTNESS:P7-INTEGRATION",
        evidence_authority=StrategyAuthorityRef(
            authority_id="APPROVED-COMPLETENESS-EVIDENCE",
            authority_version="V1",
        ),
        complete=True,
    )
    return evaluate_completeness_readiness(
        requirement=requirement,
        evidence=evidence,
        runtime_authority_class=CompletenessAuthorityClass.PRODUCTION,
    )


def cohort_membership(
    item: StrategyInstance,
) -> RequiredCohortMembershipEvidence:
    return RequiredCohortMembershipEvidence(
        evidence_id="COHORT-P7-INTEGRATION",
        cohort_id="COHORT-P7",
        policy=DecisionPolicyAuthorityRef(
            policy_id="DECISION-POLICY",
            policy_version="DP-1",
            authority=StrategyAuthorityRef(
                authority_id="DECISION-DOMAIN",
                authority_version="V1",
            ),
            authority_class=DecisionPolicyAuthorityClass.PRODUCTION,
        ),
        required_strategy_instance_ids=(
            item.strategy_instance_id,
        ),
        currentness_evidence_ref="POLICY-CURRENTNESS-P7",
    )


def test_p7_positive_authority_chain_c16_to_c18() -> None:
    item = governing_instance()

    # C16 accepted identity/config/implementation/binding authority is consumed,
    # not redefined by P7.
    registry = StrategyRegistry()
    registry.register(
        item.strategy_id,
        item.implementation_revision,
        lambda **kwargs: kwargs,
    )
    definition = registry.validate_governing_instance(item)
    assert definition.strategy_id == item.strategy_id
    assert definition.version == item.implementation_revision

    # C17 exact durable PRE_TRANSITION authority.
    transition = transition_authority(item)
    transition_state = evaluate_governing_transition(
        authority=transition,
        source_instance=item,
        durable_state=source_state(item),
    )
    assert transition_state is StrategyGoverningTransitionState.PRE_TRANSITION

    # C19 positive applicability proof.
    k520 = k520_applicability(item)
    assert (
        k520
        is K520ApplicabilityClassification.NOT_APPLICABLE_PROVEN
    )

    # C20 approved exact completeness evidence.
    completeness = completeness_ready()
    assert completeness is CompletenessReadiness.READY

    # C18 composes distinct account/restore/strategy/cohort layers.
    restore = StrategyRestoreValidEvidence(
        evidence_id="RESTORE-P7-INTEGRATION",
        strategy_instance_id=item.strategy_instance_id,
        governing_context=transition.source_context,
        restore_authority_ref="RESTORE-AUTH:P7-INTEGRATION",
        valid=True,
    )
    strategy_result = evaluate_strategy_trading_readiness(
        instance=item,
        broker_account=BrokerAccountExecutionReadyInput(
            authority_ref="W4R-D:C15:ACCOUNT-READY",
            ready=True,
        ),
        restore=restore,
        transition_state=transition_state,
        transition_authority=transition,
        k520_applicability=k520,
        k520_evidence=None,
        completeness_readiness=completeness,
    )
    assert strategy_result.strategy_restore_valid is True
    assert strategy_result.strategy_trading_ready is True
    assert strategy_result.decision_policy_version == "DP-1"

    cohort = evaluate_decision_cohort_trading_readiness(
        membership=cohort_membership(item),
        strategy_readiness=(strategy_result,),
        runtime_authority_class=DecisionPolicyAuthorityClass.PRODUCTION,
    )
    assert cohort.decision_cohort_trading_ready is True


def test_p7_c17_in_progress_blocks_strategy_and_cohort_readiness() -> None:
    item = governing_instance()
    transition = transition_authority(
        item,
        in_progress=True,
    )
    transition_state = evaluate_governing_transition(
        authority=transition,
        source_instance=item,
        durable_state=source_state(item),
    )
    assert (
        transition_state
        is StrategyGoverningTransitionState.TRANSITION_IN_PROGRESS
    )

    strategy_result = evaluate_strategy_trading_readiness(
        instance=item,
        broker_account=BrokerAccountExecutionReadyInput(
            authority_ref="W4R-D:C15:ACCOUNT-READY",
            ready=True,
        ),
        restore=StrategyRestoreValidEvidence(
            evidence_id="RESTORE-P7-IN-PROGRESS",
            strategy_instance_id=item.strategy_instance_id,
            governing_context=transition.source_context,
            restore_authority_ref="RESTORE-AUTH:P7-IN-PROGRESS",
            valid=True,
        ),
        transition_state=transition_state,
        transition_authority=transition,
        k520_applicability=k520_applicability(item),
        k520_evidence=None,
        completeness_readiness=completeness_ready(),
    )
    assert strategy_result.strategy_trading_ready is False

    cohort = evaluate_decision_cohort_trading_readiness(
        membership=cohort_membership(item),
        strategy_readiness=(strategy_result,),
        runtime_authority_class=DecisionPolicyAuthorityClass.PRODUCTION,
    )
    assert cohort.decision_cohort_trading_ready is False


@pytest.mark.parametrize(
    "k520,completeness",
    (
        (
            K520ApplicabilityClassification.UNKNOWN,
            CompletenessReadiness.READY,
        ),
        (
            K520ApplicabilityClassification.NOT_APPLICABLE_PROVEN,
            CompletenessReadiness.NOT_READY,
        ),
    ),
)
def test_p7_downstream_dependency_failure_remains_fail_closed(
    k520: K520ApplicabilityClassification,
    completeness: CompletenessReadiness,
) -> None:
    item = governing_instance()
    transition = transition_authority(item)

    result = evaluate_strategy_trading_readiness(
        instance=item,
        broker_account=BrokerAccountExecutionReadyInput(
            authority_ref="W4R-D:C15:ACCOUNT-READY",
            ready=True,
        ),
        restore=StrategyRestoreValidEvidence(
            evidence_id="RESTORE-P7-FAIL-CLOSED",
            strategy_instance_id=item.strategy_instance_id,
            governing_context=transition.source_context,
            restore_authority_ref="RESTORE-AUTH:P7-FAIL-CLOSED",
            valid=True,
        ),
        transition_state=StrategyGoverningTransitionState.PRE_TRANSITION,
        transition_authority=transition,
        k520_applicability=k520,
        k520_evidence=None,
        completeness_readiness=completeness,
    )

    assert result.strategy_trading_ready is False


def test_p7_missing_cohort_authority_and_catch_up_never_promote_live_action() -> None:
    item = governing_instance()
    transition = transition_authority(item)

    strategy_result = evaluate_strategy_trading_readiness(
        instance=item,
        broker_account=BrokerAccountExecutionReadyInput(
            authority_ref="W4R-D:C15:ACCOUNT-READY",
            ready=True,
        ),
        restore=StrategyRestoreValidEvidence(
            evidence_id="RESTORE-P7-NO-COHORT",
            strategy_instance_id=item.strategy_instance_id,
            governing_context=transition.source_context,
            restore_authority_ref="RESTORE-AUTH:P7-NO-COHORT",
            valid=True,
        ),
        transition_state=StrategyGoverningTransitionState.PRE_TRANSITION,
        transition_authority=transition,
        k520_applicability=k520_applicability(item),
        k520_evidence=None,
        completeness_readiness=completeness_ready(),
    )
    assert strategy_result.strategy_trading_ready is True

    cohort = evaluate_decision_cohort_trading_readiness(
        membership=None,
        strategy_readiness=(strategy_result,),
        runtime_authority_class=DecisionPolicyAuthorityClass.PRODUCTION,
    )
    assert cohort.decision_cohort_trading_ready is False

    isolated = evaluate_generic_startup_catch_up_output(
        output_kind=(
            StartupCatchUpOutputKind.NORMAL_BROKER_BOUND_ORDER_INTENT
        ),
        action_label="PROTECTIVE",
    )
    assert isolated.recovery_isolated is True
    assert isolated.normal_material_action_allowed is False
    assert isolated.historical_signal_promotable is False
