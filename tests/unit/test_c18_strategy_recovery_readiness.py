from __future__ import annotations

import pytest

from strategy.instance import (
    CanonicalInstrumentBindingProvenance,
    StrategyInstance,
    config_fingerprint,
)
from strategy.recovery import (
    BrokerAccountExecutionReadyInput,
    CompletenessReadiness,
    DecisionPolicyAuthorityClass,
    DecisionPolicyAuthorityRef,
    K520ApplicabilityClassification,
    K520RecoveryEvidenceRef,
    RequiredCohortMembershipEvidence,
    StartupCatchUpOutputKind,
    StrategyAuthorityRef,
    StrategyGoverningContext,
    StrategyGoverningTransitionAuthority,
    StrategyGoverningTransitionState,
    StrategyRestoreValidEvidence,
    StrategyStateSchemaReference,
    evaluate_decision_cohort_trading_readiness,
    evaluate_generic_startup_catch_up_output,
    evaluate_strategy_trading_readiness,
)


def binding() -> CanonicalInstrumentBindingProvenance:
    return CanonicalInstrumentBindingProvenance(
        instrument_id=101,
        authority_id="CANONICAL-INSTRUMENT-PROVISIONING",
        authority_version="V1",
        reference_id="BIND-C18",
    )


def instance(
    strategy_instance_id: str = "SI-1",
) -> StrategyInstance:
    config = {
        "symbol": "TX",
        "timeframe": "1m",
    }
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


def governing_context(
    item: StrategyInstance,
    *,
    config_version: str | None = None,
    config_fingerprint_value: str | None = None,
    policy_version: str = "DP-1",
) -> StrategyGoverningContext:
    return StrategyGoverningContext(
        strategy_instance_id=item.strategy_instance_id,
        strategy_id=item.strategy_id,
        config_authority=StrategyAuthorityRef(
            authority_id="STRATEGY-CONFIG",
            authority_version=(
                config_version
                if config_version is not None
                else item.config_version
            ),
        ),
        config_version=(
            config_version
            if config_version is not None
            else item.config_version
        ),
        config_fingerprint=(
            config_fingerprint_value
            if config_fingerprint_value is not None
            else item.config_fingerprint
        ),
        implementation_revision=item.implementation_revision,
        instrument_id=item.instrument_id,
        instrument_binding_provenance=item.instrument_binding_provenance,
        timeframe=item.timeframe,
        decision_policy_version=policy_version,
        state_schema_reference=StrategyStateSchemaReference(
            strategy_id=item.strategy_id,
            schema_version=1,
        ),
    )


def restore_evidence(
    item: StrategyInstance,
    *,
    valid: bool = True,
    context: StrategyGoverningContext | None = None,
) -> StrategyRestoreValidEvidence:
    return StrategyRestoreValidEvidence(
        evidence_id=f"RESTORE:{item.strategy_instance_id}",
        strategy_instance_id=item.strategy_instance_id,
        governing_context=(
            context
            if context is not None
            else governing_context(item)
        ),
        restore_authority_ref=f"RESTORE-AUTH:{item.strategy_instance_id}",
        valid=valid,
    )


def account_ready(
    ready: bool = True,
) -> BrokerAccountExecutionReadyInput:
    return BrokerAccountExecutionReadyInput(
        authority_ref="W4R-D:C15:ACCOUNT-READY",
        ready=ready,
    )


def k520_evidence(
    context: StrategyGoverningContext,
    *,
    ready: bool = True,
) -> K520RecoveryEvidenceRef:
    return K520RecoveryEvidenceRef(
        evidence_ref="K520:GAP-09:APPROVED",
        strategy_instance_id=context.strategy_instance_id,
        config_version=context.config_version,
        config_fingerprint=context.config_fingerprint,
        implementation_revision=context.implementation_revision,
        instrument_id=context.instrument_id,
        timeframe=context.timeframe,
        authority=StrategyAuthorityRef(
            authority_id="K520-RECOVERY-EVIDENCE",
            authority_version="V1",
        ),
        ready=ready,
    )


def strategy_ready(
    item: StrategyInstance,
    *,
    broker_ready: bool = True,
    restore_valid: bool = True,
    context: StrategyGoverningContext | None = None,
    transition_state: StrategyGoverningTransitionState | None = None,
    transition_authority: StrategyGoverningTransitionAuthority | None = None,
    k520: K520ApplicabilityClassification = (
        K520ApplicabilityClassification.NOT_APPLICABLE_PROVEN
    ),
    k520_ref: K520RecoveryEvidenceRef | None = None,
    completeness: CompletenessReadiness = CompletenessReadiness.READY,
):
    return evaluate_strategy_trading_readiness(
        instance=item,
        broker_account=account_ready(broker_ready),
        restore=restore_evidence(
            item,
            valid=restore_valid,
            context=context,
        ),
        transition_state=transition_state,
        transition_authority=transition_authority,
        k520_applicability=k520,
        k520_evidence=k520_ref,
        completeness_readiness=completeness,
    )


def membership(
    required: tuple[str, ...],
    *,
    authority_class: DecisionPolicyAuthorityClass = (
        DecisionPolicyAuthorityClass.PRODUCTION
    ),
) -> RequiredCohortMembershipEvidence:
    return RequiredCohortMembershipEvidence(
        evidence_id="COHORT-EVIDENCE-1",
        cohort_id="COHORT-1",
        policy=DecisionPolicyAuthorityRef(
            policy_id="DECISION-POLICY",
            policy_version="DP-1",
            authority=StrategyAuthorityRef(
                authority_id="DECISION-DOMAIN",
                authority_version="V1",
            ),
            authority_class=authority_class,
        ),
        required_strategy_instance_ids=required,
        currentness_evidence_ref="POLICY-CURRENTNESS-1",
    )


def in_progress_transition(
    item: StrategyInstance,
) -> StrategyGoverningTransitionAuthority:
    source = governing_context(item)
    target_config = {
        "symbol": "TX",
        "timeframe": "1m",
        "mode": "target",
    }
    target = governing_context(
        item,
        config_version="C2",
        config_fingerprint_value=config_fingerprint(target_config),
        policy_version="DP-2",
    )
    return StrategyGoverningTransitionAuthority(
        transition_id="TR-C18",
        strategy_instance_id=item.strategy_instance_id,
        source_context=source,
        target_context=target,
        compatibility_authority=StrategyAuthorityRef(
            authority_id="STRATEGY-COMPATIBILITY",
            authority_version="V1",
        ),
        transition_policy=StrategyAuthorityRef(
            authority_id="GOVERNING-TRANSITION",
            authority_version="V1",
        ),
        begin_effective_boundary_ref="BEGIN-C18",
    )


def test_broker_account_ready_does_not_imply_strategy_ready_when_restore_invalid() -> None:
    item = instance()

    result = strategy_ready(
        item,
        broker_ready=True,
        restore_valid=False,
    )

    assert result.broker_account_execution_ready is True
    assert result.strategy_restore_valid is False
    assert result.strategy_trading_ready is False


def test_restore_valid_with_c17_transition_in_progress_is_not_ready() -> None:
    item = instance()
    authority = in_progress_transition(item)

    result = strategy_ready(
        item,
        context=authority.source_context,
        transition_state=(
            StrategyGoverningTransitionState.TRANSITION_IN_PROGRESS
        ),
        transition_authority=authority,
    )

    assert result.strategy_restore_valid is True
    assert result.strategy_trading_ready is False
    assert "transition is in progress" in result.reasons[0]


def test_stale_configuration_is_not_strategy_ready() -> None:
    item = instance()
    stale_config = {
        "symbol": "TX",
        "timeframe": "1m",
        "stale": True,
    }
    stale = governing_context(
        item,
        config_version="C0",
        config_fingerprint_value=config_fingerprint(stale_config),
    )

    result = strategy_ready(
        item,
        context=stale,
    )

    assert result.strategy_trading_ready is False
    assert any("stale or mismatched" in reason for reason in result.reasons)


def test_c19_unknown_is_not_strategy_ready() -> None:
    result = strategy_ready(
        instance(),
        k520=K520ApplicabilityClassification.UNKNOWN,
    )

    assert result.strategy_trading_ready is False
    assert any("K520 applicability is unknown" in reason for reason in result.reasons)


def test_c19_required_without_approved_k520_evidence_is_not_ready() -> None:
    result = strategy_ready(
        instance(),
        k520=K520ApplicabilityClassification.REQUIRED,
        k520_ref=None,
    )

    assert result.strategy_trading_ready is False
    assert any("required K520 recovery evidence" in reason for reason in result.reasons)


def test_c19_required_with_exact_approved_evidence_can_satisfy_dependency() -> None:
    item = instance()
    context = governing_context(item)

    result = strategy_ready(
        item,
        context=context,
        k520=K520ApplicabilityClassification.REQUIRED,
        k520_ref=k520_evidence(context),
    )

    assert result.strategy_trading_ready is True


def test_c20_not_ready_blocks_strategy_trading_ready() -> None:
    result = strategy_ready(
        instance(),
        completeness=CompletenessReadiness.NOT_READY,
    )

    assert result.strategy_trading_ready is False
    assert any("completeness dependency" in reason for reason in result.reasons)


def test_missing_authoritative_production_cohort_authority_is_false() -> None:
    result = evaluate_decision_cohort_trading_readiness(
        membership=None,
        strategy_readiness=(
            strategy_ready(instance()),
        ),
        runtime_authority_class=DecisionPolicyAuthorityClass.PRODUCTION,
    )

    assert result.decision_cohort_trading_ready is False


def test_required_cohort_member_missing_is_false_and_not_silently_dropped() -> None:
    si1 = instance("SI-1")

    result = evaluate_decision_cohort_trading_readiness(
        membership=membership(("SI-1", "SI-2")),
        strategy_readiness=(
            strategy_ready(si1),
        ),
        runtime_authority_class=DecisionPolicyAuthorityClass.PRODUCTION,
    )

    assert result.decision_cohort_trading_ready is False
    assert result.missing_strategy_instance_ids == ("SI-2",)


def test_caller_extra_strategy_cannot_substitute_required_member() -> None:
    si1 = instance("SI-1")
    extra = instance("EXTRA")

    result = evaluate_decision_cohort_trading_readiness(
        membership=membership(("SI-1", "SI-2")),
        strategy_readiness=(
            strategy_ready(si1),
            strategy_ready(extra),
        ),
        runtime_authority_class=DecisionPolicyAuthorityClass.PRODUCTION,
    )

    assert result.decision_cohort_trading_ready is False
    assert result.missing_strategy_instance_ids == ("SI-2",)


def test_strategy_ready_does_not_imply_cohort_ready() -> None:
    si1 = instance("SI-1")

    individual = strategy_ready(si1)
    assert individual.strategy_trading_ready is True

    cohort = evaluate_decision_cohort_trading_readiness(
        membership=membership(("SI-1", "SI-2")),
        strategy_readiness=(individual,),
        runtime_authority_class=DecisionPolicyAuthorityClass.PRODUCTION,
    )

    assert cohort.decision_cohort_trading_ready is False


def test_required_member_policy_version_mismatch_is_not_cohort_ready() -> None:
    item = instance()
    context = governing_context(
        item,
        policy_version="DP-OLD",
    )

    individual = strategy_ready(
        item,
        context=context,
    )
    assert individual.strategy_trading_ready is True

    cohort = evaluate_decision_cohort_trading_readiness(
        membership=membership((item.strategy_instance_id,)),
        strategy_readiness=(individual,),
        runtime_authority_class=DecisionPolicyAuthorityClass.PRODUCTION,
    )

    assert cohort.decision_cohort_trading_ready is False
    assert cohort.not_ready_strategy_instance_ids == (
        item.strategy_instance_id,
    )


def test_test_policy_authority_cannot_promote_production_cohort() -> None:
    item = instance()

    cohort = evaluate_decision_cohort_trading_readiness(
        membership=membership(
            (item.strategy_instance_id,),
            authority_class=DecisionPolicyAuthorityClass.TEST,
        ),
        strategy_readiness=(
            strategy_ready(item),
        ),
        runtime_authority_class=DecisionPolicyAuthorityClass.PRODUCTION,
    )

    assert cohort.decision_cohort_trading_ready is False


def test_complete_required_cohort_can_be_ready_without_becoming_policy_owner() -> None:
    si1 = instance("SI-1")
    si2 = instance("SI-2")

    result = evaluate_decision_cohort_trading_readiness(
        membership=membership(("SI-1", "SI-2")),
        strategy_readiness=(
            strategy_ready(si1),
            strategy_ready(si2),
        ),
        runtime_authority_class=DecisionPolicyAuthorityClass.PRODUCTION,
    )

    assert result.decision_cohort_trading_ready is True


@pytest.mark.parametrize(
    "output_kind",
    (
        StartupCatchUpOutputKind.HISTORICAL_SIGNAL,
        StartupCatchUpOutputKind.NORMAL_BROKER_BOUND_ORDER_INTENT,
        StartupCatchUpOutputKind.NORMAL_MATERIAL_PENDING,
        StartupCatchUpOutputKind.NORMAL_BROKER_SIDE_EFFECT,
        StartupCatchUpOutputKind.CURRENT_TRADABLE_DECISION,
    ),
)
def test_generic_startup_catch_up_output_remains_recovery_isolated(
    output_kind: StartupCatchUpOutputKind,
) -> None:
    result = evaluate_generic_startup_catch_up_output(
        output_kind=output_kind,
    )

    assert result.recovery_isolated is True
    assert result.normal_material_action_allowed is False
    assert result.historical_signal_promotable is False


@pytest.mark.parametrize(
    "label",
    (
        "REDUCE",
        "EXIT",
        "SAFETY",
        "PROTECTIVE",
    ),
)
def test_action_label_cannot_bypass_catch_up_isolation(
    label: str,
) -> None:
    result = evaluate_generic_startup_catch_up_output(
        output_kind=(
            StartupCatchUpOutputKind.NORMAL_BROKER_BOUND_ORDER_INTENT
        ),
        action_label=label,
    )

    assert result.normal_material_action_allowed is False
    assert result.recovery_isolated is True
