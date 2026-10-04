from __future__ import annotations

import pytest
from pydantic import ValidationError

from strategy.instance import (
    CanonicalInstrumentBindingProvenance,
    StrategyInstance,
    config_fingerprint,
)
from strategy.recovery import (
    K520ApplicabilityClassification,
    K520ApplicabilityEvidence,
    StrategyAuthorityRef,
    evaluate_k520_applicability,
)


MOR1_A = "mor1_" + ("a" * 64)
MOR1_B = "mor1_" + ("b" * 64)


def instance() -> StrategyInstance:
    config = {"symbol": "TX", "timeframe": "1m"}
    return StrategyInstance(
        strategy_instance_id="SI-C19",
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
                reference_id="BIND-C19",
            )
        ),
    )


def evidence(
    *,
    claim: K520ApplicabilityClassification = (
        K520ApplicabilityClassification.NOT_APPLICABLE_PROVEN
    ),
    **updates,
) -> K520ApplicabilityEvidence:
    item = instance()
    values = dict(
        evidence_id="K520-EVIDENCE-C19",
        strategy_instance_id=item.strategy_instance_id,
        strategy_id=item.strategy_id,
        config_version=item.config_version,
        config_fingerprint=item.config_fingerprint,
        implementation_revision=item.implementation_revision,
        instrument_id=item.instrument_id,
        instrument_binding_provenance=item.instrument_binding_provenance,
        timeframe=item.timeframe,
        feature_dependency_contract=StrategyAuthorityRef(
            authority_id="FEATURE-DEPENDENCY-CONTRACT",
            authority_version="V1",
        ),
        classification_claim=claim,
        required_replay_horizon=520,
        available_replay_horizon=520,
        governing_observation_frontier_revision_id=MOR1_A,
        evaluated_observation_frontier_revision_id=MOR1_A,
        current_observation_frontier_revision_id=MOR1_A,
        causal_frontier_ref="CAUSAL-FRONTIER-C19",
        currentness_evidence_ref="CURRENTNESS-C19",
        proof_authority=StrategyAuthorityRef(
            authority_id="K520-APPLICABILITY-PROOF",
            authority_version="V1",
        ),
    )
    values.update(updates)
    return K520ApplicabilityEvidence(**values)


def test_c19_has_exactly_three_applicability_classifications() -> None:
    assert tuple(
        item.value for item in K520ApplicabilityClassification
    ) == (
        "NOT_APPLICABLE_PROVEN",
        "REQUIRED",
        "UNKNOWN",
    )


def test_not_applicable_requires_complete_positive_exact_proof() -> None:
    assert evaluate_k520_applicability(
        instance=instance(),
        evidence=evidence(),
    ) is K520ApplicabilityClassification.NOT_APPLICABLE_PROVEN


def test_required_is_valid_and_does_not_claim_k520_recovery_complete() -> None:
    assert evaluate_k520_applicability(
        instance=instance(),
        evidence=evidence(
            claim=K520ApplicabilityClassification.REQUIRED
        ),
    ) is K520ApplicabilityClassification.REQUIRED


def test_unknown_dependency_fails_closed() -> None:
    assert evaluate_k520_applicability(
        instance=instance(),
        evidence=evidence(feature_dependency_contract=None),
    ) is K520ApplicabilityClassification.UNKNOWN


def test_insufficient_reconstruction_horizon_fails_closed() -> None:
    assert evaluate_k520_applicability(
        instance=instance(),
        evidence=evidence(available_replay_horizon=519),
    ) is K520ApplicabilityClassification.UNKNOWN


def test_historical_or_corrected_observation_frontier_fails_closed() -> None:
    assert evaluate_k520_applicability(
        instance=instance(),
        evidence=evidence(
            current_observation_frontier_revision_id=MOR1_B,
        ),
    ) is K520ApplicabilityClassification.UNKNOWN


def test_implementation_drift_fails_closed() -> None:
    assert evaluate_k520_applicability(
        instance=instance(),
        evidence=evidence(implementation_revision="2.0.0"),
    ) is K520ApplicabilityClassification.UNKNOWN


def test_missing_causal_frontier_fails_closed() -> None:
    assert evaluate_k520_applicability(
        instance=instance(),
        evidence=evidence(causal_frontier_ref=None),
    ) is K520ApplicabilityClassification.UNKNOWN


def test_unknown_claim_never_promotes_even_with_other_positive_evidence() -> None:
    assert evaluate_k520_applicability(
        instance=instance(),
        evidence=evidence(
            claim=K520ApplicabilityClassification.UNKNOWN,
        ),
    ) is K520ApplicabilityClassification.UNKNOWN


@pytest.mark.parametrize(
    "heuristic",
    (
        "appears_stateless",
        "missing_feature_payload",
        "replay_completed",
        "no_exception",
        "no_feature_cache",
    ),
)
def test_heuristic_non_authorities_cannot_enter_applicability_contract(
    heuristic: str,
) -> None:
    with pytest.raises(ValidationError):
        K520ApplicabilityEvidence(
            **{
                **evidence().model_dump(),
                heuristic: True,
            }
        )


def test_non_mor1_frontier_is_rejected_as_noncanonical_authority() -> None:
    with pytest.raises(
        ValidationError,
        match="mor1 revision identity",
    ):
        evidence(
            governing_observation_frontier_revision_id="BAR-1",
        )
