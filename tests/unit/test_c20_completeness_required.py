from __future__ import annotations

import pytest
from pydantic import ValidationError

from strategy.recovery import (
    CompletenessAuthorityClass,
    CompletenessEvidenceAuthority,
    CompletenessReadiness,
    CompletenessRequirementAuthority,
    CompletenessRequirementClassification,
    StrategyAuthorityRef,
    evaluate_completeness_readiness,
)


MOR1_A = "mor1_" + ("a" * 64)
MOR1_B = "mor1_" + ("b" * 64)


def requirement(
    *,
    classification: CompletenessRequirementClassification = (
        CompletenessRequirementClassification.REQUIRED
    ),
    authority_class: CompletenessAuthorityClass = (
        CompletenessAuthorityClass.PRODUCTION
    ),
    **updates,
) -> CompletenessRequirementAuthority:
    values = dict(
        requirement_id="COMPLETENESS-REQ-C20",
        consumer_ref="STRATEGY-INSTANCE:SI-C20",
        scope_ref="INSTRUMENT:101/TIMEFRAME:1m",
        stream_ref="MARKET-OBSERVATION:PRIMARY",
        horizon_ref="HORIZON:RECOVERY-CUT",
        policy_authority=StrategyAuthorityRef(
            authority_id="COMPLETENESS-REQUIREMENT-POLICY",
            authority_version="V1",
        ),
        authority_class=authority_class,
        classification=classification,
    )
    values.update(updates)
    return CompletenessRequirementAuthority(**values)


def evidence(
    *,
    authority_class: CompletenessAuthorityClass = (
        CompletenessAuthorityClass.PRODUCTION
    ),
    complete: bool = True,
    **updates,
) -> CompletenessEvidenceAuthority:
    values = dict(
        evidence_id="COMPLETENESS-EVIDENCE-C20",
        consumer_ref="STRATEGY-INSTANCE:SI-C20",
        scope_ref="INSTRUMENT:101/TIMEFRAME:1m",
        stream_ref="MARKET-OBSERVATION:PRIMARY",
        horizon_ref="HORIZON:RECOVERY-CUT",
        policy_authority=StrategyAuthorityRef(
            authority_id="COMPLETENESS-REQUIREMENT-POLICY",
            authority_version="V1",
        ),
        authority_class=authority_class,
        evaluated_world_ref="WORLD:RECOVERY-CUT-1",
        current_world_ref="WORLD:RECOVERY-CUT-1",
        evaluated_frontier_revision_id=MOR1_A,
        current_frontier_revision_id=MOR1_A,
        currentness_evidence_ref="CURRENTNESS:C20-1",
        evidence_authority=StrategyAuthorityRef(
            authority_id="APPROVED-COMPLETENESS-EVIDENCE",
            authority_version="V1",
        ),
        complete=complete,
    )
    values.update(updates)
    return CompletenessEvidenceAuthority(**values)


def test_c20_requirement_classification_is_exact() -> None:
    assert tuple(
        item.value for item in CompletenessRequirementClassification
    ) == (
        "NOT_REQUIRED_PROVEN",
        "REQUIRED",
        "UNKNOWN",
    )


def test_c20_authority_classes_are_exact_and_non_promotable() -> None:
    assert tuple(
        item.value for item in CompletenessAuthorityClass
    ) == (
        "TEST",
        "SANDBOX",
        "PRODUCTION",
    )


def test_missing_or_unknown_requirement_fails_closed() -> None:
    assert evaluate_completeness_readiness(
        requirement=None,
        evidence=None,
        runtime_authority_class=CompletenessAuthorityClass.PRODUCTION,
    ) is CompletenessReadiness.NOT_READY

    assert evaluate_completeness_readiness(
        requirement=requirement(
            classification=CompletenessRequirementClassification.UNKNOWN,
        ),
        evidence=evidence(),
        runtime_authority_class=CompletenessAuthorityClass.PRODUCTION,
    ) is CompletenessReadiness.NOT_READY


def test_not_required_requires_positive_requirement_authority_only() -> None:
    assert evaluate_completeness_readiness(
        requirement=requirement(
            classification=(
                CompletenessRequirementClassification.NOT_REQUIRED_PROVEN
            )
        ),
        evidence=None,
        runtime_authority_class=CompletenessAuthorityClass.PRODUCTION,
    ) is CompletenessReadiness.READY


def test_required_without_approved_evidence_is_not_ready() -> None:
    assert evaluate_completeness_readiness(
        requirement=requirement(),
        evidence=None,
        runtime_authority_class=CompletenessAuthorityClass.PRODUCTION,
    ) is CompletenessReadiness.NOT_READY


def test_required_exact_complete_current_evidence_is_ready() -> None:
    assert evaluate_completeness_readiness(
        requirement=requirement(),
        evidence=evidence(),
        runtime_authority_class=CompletenessAuthorityClass.PRODUCTION,
    ) is CompletenessReadiness.READY


@pytest.mark.parametrize(
    "field,value",
    (
        ("consumer_ref", "STRATEGY-INSTANCE:OTHER"),
        ("scope_ref", "INSTRUMENT:999/TIMEFRAME:1m"),
        ("stream_ref", "MARKET-OBSERVATION:OTHER"),
        ("horizon_ref", "HORIZON:OTHER"),
        (
            "policy_authority",
            StrategyAuthorityRef(
                authority_id="COMPLETENESS-REQUIREMENT-POLICY",
                authority_version="V2",
            ),
        ),
    ),
)
def test_required_evidence_must_bind_exact_requirement_world(
    field: str,
    value: object,
) -> None:
    assert evaluate_completeness_readiness(
        requirement=requirement(),
        evidence=evidence(**{field: value}),
        runtime_authority_class=CompletenessAuthorityClass.PRODUCTION,
    ) is CompletenessReadiness.NOT_READY


@pytest.mark.parametrize(
    "evidence_class",
    (
        CompletenessAuthorityClass.TEST,
        CompletenessAuthorityClass.SANDBOX,
    ),
)
def test_non_production_evidence_cannot_promote_to_production(
    evidence_class: CompletenessAuthorityClass,
) -> None:
    assert evaluate_completeness_readiness(
        requirement=requirement(),
        evidence=evidence(authority_class=evidence_class),
        runtime_authority_class=CompletenessAuthorityClass.PRODUCTION,
    ) is CompletenessReadiness.NOT_READY


def test_test_requirement_authority_cannot_be_used_in_production() -> None:
    assert evaluate_completeness_readiness(
        requirement=requirement(
            authority_class=CompletenessAuthorityClass.TEST,
        ),
        evidence=evidence(
            authority_class=CompletenessAuthorityClass.TEST,
        ),
        runtime_authority_class=CompletenessAuthorityClass.PRODUCTION,
    ) is CompletenessReadiness.NOT_READY


def test_incomplete_evidence_is_not_ready() -> None:
    assert evaluate_completeness_readiness(
        requirement=requirement(),
        evidence=evidence(complete=False),
        runtime_authority_class=CompletenessAuthorityClass.PRODUCTION,
    ) is CompletenessReadiness.NOT_READY


def test_stale_world_or_frontier_is_not_ready() -> None:
    assert evaluate_completeness_readiness(
        requirement=requirement(),
        evidence=evidence(
            current_world_ref="WORLD:NEWER",
        ),
        runtime_authority_class=CompletenessAuthorityClass.PRODUCTION,
    ) is CompletenessReadiness.NOT_READY

    assert evaluate_completeness_readiness(
        requirement=requirement(),
        evidence=evidence(
            current_frontier_revision_id=MOR1_B,
        ),
        runtime_authority_class=CompletenessAuthorityClass.PRODUCTION,
    ) is CompletenessReadiness.NOT_READY


def test_non_mor1_frontier_is_rejected() -> None:
    with pytest.raises(
        ValidationError,
        match="mor1 revision identity",
    ):
        evidence(
            evaluated_frontier_revision_id="BAR-1",
        )


@pytest.mark.parametrize(
    "forbidden",
    (
        "no_candidate",
        "r14_complete",
        "fake_provider",
        "data_health_service",
        "detector_result",
    ),
)
def test_non_authoritative_shortcuts_cannot_enter_c20_contract(
    forbidden: str,
) -> None:
    with pytest.raises(ValidationError):
        CompletenessEvidenceAuthority(
            **{
                **evidence().model_dump(),
                forbidden: True,
            }
        )
