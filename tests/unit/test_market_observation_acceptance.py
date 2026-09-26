from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from domain.market_observation import (
    build_market_observation_revision_id,
    canonicalize_market_observation_content,
    canonicalize_market_observation_logical_key,
)
from domain.market_observation_acceptance import (
    MarketObservationAcceptanceContractError,
    MarketObservationAcceptancePolicy,
    MarketObservationCandidateEvidence,
    MarketObservationDecisionKind,
    MarketObservationRoutingRole,
    MarketObservationSourcePolicyRule,
    evaluate_market_observation_candidate,
)


NOW = datetime(
    2026,
    9,
    26,
    2,
    0,
    tzinfo=timezone.utc,
)


def _key():
    return canonicalize_market_observation_logical_key(
        instrument_id=1,
        contract_id=101,
        requires_contract_id=True,
        timeframe="1m",
        interval_start_at=datetime(
            2026,
            9,
            26,
            1,
            tzinfo=timezone.utc,
        ),
    )


def _content(
    *,
    close: str = "20030",
):
    return canonicalize_market_observation_content(
        open="20000",
        high="20050",
        low="19980",
        close=close,
        volume=100,
        amount="2003000",
        trade_count=50,
        tick_count=None,
        trade_date=date(2026, 9, 26),
        session_ref="DAY",
    )


def _rule(
    source_id: str = "SRC-A",
    *,
    eligible: bool = True,
    seed: bool = True,
    authoritative: bool = False,
    correction: bool = True,
):
    return MarketObservationSourcePolicyRule(
        source_id=source_id,
        evidence_eligible=eligible,
        can_seed_initial_truth=seed,
        authoritative_for_scope=authoritative,
        can_accept_formal_correction=correction,
    )


def _policy(
    *rules,
    version: int = 1,
):
    return MarketObservationAcceptancePolicy(
        policy_id="POL-MARKET-1",
        version=version,
        scope_ref="TXF-1M",
        source_rules=(
            tuple(rules)
            if rules
            else (_rule(),)
        ),
    )


def _candidate(
    candidate_id: str,
    *,
    source_id: str = "SRC-A",
    role: MarketObservationRoutingRole = (
        MarketObservationRoutingRole.PRIMARY
    ),
    close: str = "20030",
    correction_ref: str | None = None,
    provenance: dict[str, object] | None = None,
    policy_version: int = 1,
):
    key = _key()
    content = _content(close=close)
    fingerprint = content.content_fingerprint
    revision_id = build_market_observation_revision_id(
        logical_key=key,
        content_fingerprint=fingerprint,
    )

    return MarketObservationCandidateEvidence(
        candidate_id=candidate_id,
        logical_key=key,
        content=content,
        content_fingerprint=fingerprint,
        observation_revision_id=revision_id,
        source_id=source_id,
        routing_role=role,
        source_record_ref=f"ROW-{candidate_id}",
        formal_correction_ref=correction_ref,
        received_at=NOW,
        provenance_json=(
            {"transport": "fixture"}
            if provenance is None
            else provenance
        ),
        acceptance_policy_id="POL-MARKET-1",
        acceptance_policy_version=policy_version,
        acceptance_scope_ref="TXF-1M",
    )


def test_first_eligible_seed_is_revision_one() -> None:
    plan = evaluate_market_observation_candidate(
        policy=_policy(),
        candidate=_candidate("C-1"),
        current_revision=None,
        accepted_at=NOW,
    )

    assert (
        plan.decision_kind
        is MarketObservationDecisionKind.ACCEPTED_NEW_REVISION
    )
    assert plan.accepted_revision is not None
    assert plan.accepted_revision.revision_seq == 1
    assert plan.accepted_revision.supersedes_revision_id is None


def test_primary_routing_role_alone_does_not_grant_truth_authority() -> None:
    policy = _policy(
        _rule(
            seed=False,
            authoritative=False,
        )
    )

    plan = evaluate_market_observation_candidate(
        policy=policy,
        candidate=_candidate(
            "C-2",
            role=MarketObservationRoutingRole.PRIMARY,
        ),
        current_revision=None,
        accepted_at=NOW,
    )

    assert (
        plan.decision_kind
        is MarketObservationDecisionKind.QUARANTINED_INELIGIBLE_SOURCE
    )
    assert plan.accepted_revision is None
    assert plan.quarantined


def test_source_registry_like_authority_flag_does_not_waive_seed_rule() -> None:
    policy = _policy(
        _rule(
            seed=False,
            authoritative=True,
            correction=False,
        )
    )

    plan = evaluate_market_observation_candidate(
        policy=policy,
        candidate=_candidate("C-3"),
        current_revision=None,
        accepted_at=NOW,
    )

    assert plan.quarantined
    assert plan.accepted_revision is None


def _accepted_initial():
    plan = evaluate_market_observation_candidate(
        policy=_policy(
            _rule("SRC-A"),
            _rule("SRC-B", seed=False),
        ),
        candidate=_candidate("C-INITIAL"),
        current_revision=None,
        accepted_at=NOW,
    )

    assert plan.accepted_revision is not None
    return plan.accepted_revision


def test_same_source_same_content_is_corroboration() -> None:
    current = _accepted_initial()

    plan = evaluate_market_observation_candidate(
        policy=_policy(
            _rule("SRC-A"),
            _rule("SRC-B", seed=False),
        ),
        candidate=_candidate("C-SAME-A"),
        current_revision=current,
        accepted_at=NOW,
    )

    assert (
        plan.decision_kind
        is MarketObservationDecisionKind.CORROBORATED_EXISTING
    )
    assert plan.accepted_revision is None
    assert plan.linked_revision_id == current.observation_revision_id


def test_different_source_same_content_is_corroboration() -> None:
    current = _accepted_initial()

    plan = evaluate_market_observation_candidate(
        policy=_policy(
            _rule("SRC-A"),
            _rule("SRC-B", seed=False),
        ),
        candidate=_candidate(
            "C-SAME-B",
            source_id="SRC-B",
            role=MarketObservationRoutingRole.SECONDARY,
        ),
        current_revision=current,
        accepted_at=NOW,
    )

    assert (
        plan.decision_kind
        is MarketObservationDecisionKind.CORROBORATED_EXISTING
    )
    assert plan.accepted_revision is None
    assert plan.linked_revision_id == current.observation_revision_id


def test_reingestion_same_content_is_idempotent_at_revision_level() -> None:
    current = _accepted_initial()

    first = evaluate_market_observation_candidate(
        policy=_policy(
            _rule("SRC-A"),
            _rule("SRC-B", seed=False),
        ),
        candidate=_candidate("C-REPLAY-1"),
        current_revision=current,
        accepted_at=NOW,
    )

    second = evaluate_market_observation_candidate(
        policy=_policy(
            _rule("SRC-A"),
            _rule("SRC-B", seed=False),
        ),
        candidate=_candidate("C-REPLAY-2"),
        current_revision=current,
        accepted_at=NOW,
    )

    assert first.accepted_revision is None
    assert second.accepted_revision is None
    assert (
        first.linked_revision_id
        == second.linked_revision_id
        == current.observation_revision_id
    )


def test_provenance_only_change_does_not_create_revision() -> None:
    current = _accepted_initial()

    candidate = _candidate(
        "C-PROVENANCE",
        provenance={
            "transport": "second-ingestion",
            "checksum": "ABC",
        },
    )

    assert (
        candidate.content_fingerprint
        == current.content_fingerprint
    )

    plan = evaluate_market_observation_candidate(
        policy=_policy(
            _rule("SRC-A"),
            _rule("SRC-B", seed=False),
        ),
        candidate=candidate,
        current_revision=current,
        accepted_at=NOW,
    )

    assert (
        plan.decision_kind
        is MarketObservationDecisionKind.CORROBORATED_EXISTING
    )
    assert plan.accepted_revision is None


def test_different_content_without_formal_proof_is_quarantined() -> None:
    current = _accepted_initial()

    plan = evaluate_market_observation_candidate(
        policy=_policy(),
        candidate=_candidate(
            "C-DIFF-NO-PROOF",
            close="20031",
            correction_ref=None,
        ),
        current_revision=current,
        accepted_at=NOW,
    )

    assert (
        plan.decision_kind
        is MarketObservationDecisionKind.QUARANTINED_UNPROVEN_CORRECTION
    )
    assert plan.quarantined
    assert plan.accepted_revision is None
    assert plan.linked_revision_id == current.observation_revision_id


def test_validation_different_content_is_explicit_cross_source_conflict() -> None:
    current = _accepted_initial()

    plan = evaluate_market_observation_candidate(
        policy=_policy(
            _rule("SRC-A"),
            _rule(
                "SRC-B",
                seed=False,
                correction=False,
            ),
        ),
        candidate=_candidate(
            "C-VALIDATION-CONFLICT",
            source_id="SRC-B",
            role=MarketObservationRoutingRole.VALIDATION,
            close="20031",
        ),
        current_revision=current,
        accepted_at=NOW,
    )

    assert (
        plan.decision_kind
        is MarketObservationDecisionKind.QUARANTINED_CROSS_SOURCE_CONFLICT
    )
    assert plan.accepted_revision is None
    assert plan.linked_revision_id == current.observation_revision_id


def test_explicit_formal_correction_advances_contiguous_revision() -> None:
    current = _accepted_initial()

    plan = evaluate_market_observation_candidate(
        policy=_policy(),
        candidate=_candidate(
            "C-CORRECTION",
            close="20031",
            correction_ref="EXCHANGE-CORR-0001",
        ),
        current_revision=current,
        accepted_at=NOW,
    )

    assert (
        plan.decision_kind
        is MarketObservationDecisionKind.ACCEPTED_NEW_REVISION
    )
    assert plan.accepted_revision is not None
    assert (
        plan.accepted_revision.revision_seq
        == current.revision_seq + 1
    )
    assert (
        plan.accepted_revision.supersedes_revision_id
        == current.observation_revision_id
    )


def test_authoritative_for_scope_does_not_waive_formal_correction() -> None:
    current = _accepted_initial()

    policy = _policy(
        _rule(
            authoritative=True,
            correction=True,
        )
    )

    plan = evaluate_market_observation_candidate(
        policy=policy,
        candidate=_candidate(
            "C-AUTH-NO-CORR",
            close="20031",
            correction_ref=None,
        ),
        current_revision=current,
        accepted_at=NOW,
    )

    assert plan.quarantined
    assert plan.accepted_revision is None


def test_policy_version_change_does_not_rewrite_old_revision() -> None:
    current = _accepted_initial()

    original_policy_version = current.acceptance_policy_version

    policy_v2 = _policy(
        _rule(),
        version=2,
    )

    candidate_v2 = _candidate(
        "C-POLICY-V2",
        close="20031",
        correction_ref="FORMAL-2",
        policy_version=2,
    )

    plan = evaluate_market_observation_candidate(
        policy=policy_v2,
        candidate=candidate_v2,
        current_revision=current,
        accepted_at=NOW,
    )

    assert original_policy_version == 1
    assert current.acceptance_policy_version == 1

    assert plan.accepted_revision is not None
    assert plan.accepted_revision.acceptance_policy_version == 2


def test_quarantine_preserves_previous_accepted_revision() -> None:
    current = _accepted_initial()

    plan = evaluate_market_observation_candidate(
        policy=_policy(),
        candidate=_candidate(
            "C-QUARANTINE",
            close="20100",
        ),
        current_revision=current,
        accepted_at=NOW,
    )

    assert plan.quarantined
    assert plan.accepted_revision is None
    assert plan.linked_revision_id == current.observation_revision_id
    assert current.revision_seq == 1


def test_ineligible_source_is_quarantined_even_if_primary() -> None:
    policy = _policy(
        _rule(
            eligible=False,
            seed=True,
        )
    )

    plan = evaluate_market_observation_candidate(
        policy=policy,
        candidate=_candidate(
            "C-INELIGIBLE",
            role=MarketObservationRoutingRole.PRIMARY,
        ),
        current_revision=None,
        accepted_at=NOW,
    )

    assert (
        plan.decision_kind
        is MarketObservationDecisionKind.QUARANTINED_INELIGIBLE_SOURCE
    )


def test_candidate_policy_binding_is_exact() -> None:
    candidate = _candidate("C-BINDING")

    wrong_policy = MarketObservationAcceptancePolicy(
        policy_id="OTHER",
        version=1,
        scope_ref="TXF-1M",
        source_rules=(_rule(),),
    )

    with pytest.raises(
        MarketObservationAcceptanceContractError,
        match="policy_id",
    ):
        evaluate_market_observation_candidate(
            policy=wrong_policy,
            candidate=candidate,
            current_revision=None,
            accepted_at=NOW,
        )


def test_candidate_requires_explicit_aware_received_at() -> None:
    key = _key()
    content = _content()
    fingerprint = content.content_fingerprint
    revision_id = build_market_observation_revision_id(
        logical_key=key,
        content_fingerprint=fingerprint,
    )

    with pytest.raises(
        MarketObservationAcceptanceContractError,
        match="timezone-aware",
    ):
        MarketObservationCandidateEvidence(
            candidate_id="C-NAIVE",
            logical_key=key,
            content=content,
            content_fingerprint=fingerprint,
            observation_revision_id=revision_id,
            source_id="SRC-A",
            routing_role=MarketObservationRoutingRole.PRIMARY,
            source_record_ref=None,
            formal_correction_ref=None,
            received_at=datetime(2026, 9, 26, 2, 0),
            provenance_json={},
            acceptance_policy_id="POL-MARKET-1",
            acceptance_policy_version=1,
            acceptance_scope_ref="TXF-1M",
        )


def test_candidate_revision_identity_must_match_c23() -> None:
    first = _candidate("C-ID-1")
    second = _candidate(
        "C-ID-2",
        close="20031",
    )

    with pytest.raises(
        MarketObservationAcceptanceContractError,
        match="revision_id",
    ):
        MarketObservationCandidateEvidence(
            candidate_id="C-ID-BAD",
            logical_key=first.logical_key,
            content=first.content,
            content_fingerprint=first.content_fingerprint,
            observation_revision_id=second.observation_revision_id,
            source_id="SRC-A",
            routing_role=MarketObservationRoutingRole.PRIMARY,
            source_record_ref=None,
            formal_correction_ref=None,
            received_at=NOW,
            provenance_json={},
            acceptance_policy_id="POL-MARKET-1",
            acceptance_policy_version=1,
            acceptance_scope_ref="TXF-1M",
        )


def test_duplicate_policy_source_rule_is_rejected() -> None:
    with pytest.raises(
        MarketObservationAcceptanceContractError,
        match="duplicate",
    ):
        _policy(
            _rule("SRC-A"),
            _rule("SRC-A"),
        )
