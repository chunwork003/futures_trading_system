
from datetime import date, datetime, timezone

import pytest

from domain.market_observation import (
    build_market_observation_revision_id,
    canonicalize_market_observation_content,
    canonicalize_market_observation_logical_key,
)
from domain.market_observation_acceptance import (
    MarketObservationAcceptancePolicy,
    MarketObservationCandidateEvidence,
    MarketObservationDecisionKind,
    MarketObservationRevision,
    MarketObservationRoutingRole,
    MarketObservationSourcePolicyRule,
)
from persistence.market_observation import (
    MarketObservationAcceptanceResult,
    MarketObservationCandidateDecisionEvidence,
    MarketObservationIdentityConflictError,
)
from persistence.market_observation_delivery import (
    DurableMarketObservationStrategyDelivery,
    MarketObservationRevisionResolutionError,
    MarketObservationStrategyDeliveryBlockedError,
)


NOW = datetime(
    2026,
    9,
    26,
    3,
    tzinfo=timezone.utc,
)


def revision():
    key = (
        canonicalize_market_observation_logical_key(
            instrument_id=1,
            contract_id=101,
            requires_contract_id=True,
            timeframe="1m",
            interval_start_at=(
                datetime(
                    2026,
                    9,
                    26,
                    2,
                    tzinfo=timezone.utc,
                )
            ),
        )
    )

    content = (
        canonicalize_market_observation_content(
            open="20000",
            high="20050",
            low="19980",
            close="20030",
            volume=100,
            amount="2003000",
            trade_count=50,
            tick_count=None,
            trade_date=date(
                2026,
                9,
                26,
            ),
            session_ref="DAY",
        )
    )

    revision_id = (
        build_market_observation_revision_id(
            logical_key=key,
            content_fingerprint=(
                content.content_fingerprint
            ),
        )
    )

    return MarketObservationRevision(
        observation_revision_id=(
            revision_id
        ),
        logical_key=key,
        content=content,
        content_fingerprint=(
            content.content_fingerprint
        ),
        revision_seq=1,
        supersedes_revision_id=None,
        accepted_at=NOW,
        acceptance_policy_id="POL-1",
        acceptance_policy_version=1,
        acceptance_scope_ref="TXF-1M",
    )


def policy():
    return MarketObservationAcceptancePolicy(
        policy_id="POL-1",
        version=1,
        scope_ref="TXF-1M",
        source_rules=(
            MarketObservationSourcePolicyRule(
                source_id="SRC-A",
                evidence_eligible=True,
                can_seed_initial_truth=True,
                authoritative_for_scope=False,
                can_accept_formal_correction=True,
            ),
        ),
    )


def candidate(item):
    return MarketObservationCandidateEvidence(
        candidate_id="CAND-1",
        logical_key=item.logical_key,
        content=item.content,
        content_fingerprint=(
            item.content_fingerprint
        ),
        observation_revision_id=(
            item.observation_revision_id
        ),
        source_id="SRC-A",
        routing_role=(
            MarketObservationRoutingRole
            .PRIMARY
        ),
        source_record_ref="ROW-1",
        formal_correction_ref=None,
        received_at=NOW,
        provenance_json={
            "fixture": True,
        },
        acceptance_policy_id="POL-1",
        acceptance_policy_version=1,
        acceptance_scope_ref="TXF-1M",
    )


def result(
    item,
    *,
    kind=(
        MarketObservationDecisionKind
        .ACCEPTED_NEW_REVISION
    ),
    quarantined=False,
    integrity_error=None,
    accepted=True,
):
    decision = (
        MarketObservationCandidateDecisionEvidence(
            decision_id="DEC-1",
            candidate_id="CAND-1",
            decision_kind=kind,
            decided_at=NOW,
            linked_revision_id=(
                item.observation_revision_id
            ),
            reason=(
                "BLOCKED"
                if quarantined
                else None
            ),
            acceptance_policy_id="POL-1",
            acceptance_policy_version=1,
            acceptance_scope_ref="TXF-1M",
        )
    )

    return (
        MarketObservationAcceptanceResult(
            decision=decision,
            accepted_revision=(
                item
                if accepted
                else None
            ),
            current_revision_id=(
                item.observation_revision_id
            ),
            current_revision_seq=1,
            quarantined=quarantined,
            integrity_error=(
                integrity_error
            ),
        )
    )


class Uow:
    def __init__(
        self,
        trace,
        fail=False,
    ):
        self.trace = trace
        self.fail = fail
        self.committed = False

    def __enter__(self):
        self.trace.append(
            "enter"
        )

        return self

    def commit(self):
        self.trace.append(
            "commit"
        )

        if self.fail:
            raise RuntimeError(
                "commit failed"
            )

        self.committed = True

    def rollback(self):
        self.trace.append(
            "rollback"
        )

    def __exit__(
        self,
        typ,
        exc,
        tb,
    ):
        if not self.committed:
            self.trace.append(
                "rollback"
            )

        self.trace.append(
            "exit"
        )

        return False


class Repo:
    def __init__(
        self,
        trace,
        acceptance,
    ):
        self.trace = trace
        self.acceptance = (
            acceptance
        )

    def process_candidate(
        self,
        **kwargs,
    ):
        self.trace.append(
            "process"
        )

        return self.acceptance


def service(
    trace,
    repo,
    resolved,
    *,
    fail=False,
):
    def loader(
        revision_id,
    ):
        trace.append(
            "resolve"
        )

        if resolved is None:
            return None

        assert (
            revision_id
            == resolved.observation_revision_id
        )

        return resolved

    return (
        DurableMarketObservationStrategyDelivery(
            uow_factory=(
                lambda: Uow(
                    trace,
                    fail,
                )
            ),
            repository_factory=(
                lambda uow: repo
            ),
            revision_loader=loader,
        )
    )


def test_delivery_occurs_only_after_commit_exit_and_exact_resolution():
    item = revision()
    trace = []

    delivered = service(
        trace,
        Repo(
            trace,
            result(
                item
            ),
        ),
        item,
    ).deliver(
        policy=policy(),
        candidate=candidate(
            item
        ),
        decision_id="DEC-1",
        decided_at=NOW,
        consumer=lambda value: (
            trace.append(
                "consumer"
            ),
            "OK",
        )[1],
    )

    assert trace == [
        "enter",
        "process",
        "commit",
        "exit",
        "resolve",
        "consumer",
    ]

    assert (
        delivered.revision
        == item
    )

    assert (
        delivered
        .execution_trigger_ref
        .market_observation_revision_id
        == (
            item
            .observation_revision_id
            .value
        )
    )


def test_commit_failure_causes_zero_resolution_and_delivery():
    item = revision()
    trace = []

    with pytest.raises(
        RuntimeError,
        match="commit failed",
    ):
        service(
            trace,
            Repo(
                trace,
                result(
                    item
                ),
            ),
            item,
            fail=True,
        ).deliver(
            policy=policy(),
            candidate=candidate(
                item
            ),
            decision_id="DEC-1",
            decided_at=NOW,
            consumer=lambda value: (
                trace.append(
                    "consumer"
                )
            ),
        )

    assert "resolve" not in trace
    assert "consumer" not in trace


def test_quarantine_commits_evidence_but_blocks_delivery():
    item = revision()
    trace = []

    with pytest.raises(
        MarketObservationStrategyDeliveryBlockedError
    ):
        service(
            trace,
            Repo(
                trace,
                result(
                    item,
                    kind=(
                        MarketObservationDecisionKind
                        .QUARANTINED_UNPROVEN_CORRECTION
                    ),
                    quarantined=True,
                    accepted=False,
                ),
            ),
            item,
        ).deliver(
            policy=policy(),
            candidate=candidate(
                item
            ),
            decision_id="DEC-1",
            decided_at=NOW,
            consumer=lambda value: (
                trace.append(
                    "consumer"
                )
            ),
        )

    assert trace[:4] == [
        "enter",
        "process",
        "commit",
        "exit",
    ]

    assert "resolve" not in trace
    assert "consumer" not in trace


def test_integrity_conflict_blocks_delivery():
    item = revision()
    trace = []

    with pytest.raises(
        MarketObservationStrategyDeliveryBlockedError
    ):
        service(
            trace,
            Repo(
                trace,
                result(
                    item,
                    kind=(
                        MarketObservationDecisionKind
                        .IDENTITY_CONFLICT
                    ),
                    quarantined=True,
                    integrity_error=(
                        MarketObservationIdentityConflictError(
                            "identity conflict"
                        )
                    ),
                    accepted=False,
                ),
            ),
            item,
        ).deliver(
            policy=policy(),
            candidate=candidate(
                item
            ),
            decision_id="DEC-1",
            decided_at=NOW,
            consumer=lambda value: (
                trace.append(
                    "consumer"
                )
            ),
        )

    assert "resolve" not in trace
    assert "consumer" not in trace


def test_missing_exact_revision_after_commit_fails_closed():
    item = revision()
    trace = []

    with pytest.raises(
        MarketObservationRevisionResolutionError,
        match="exact mor1",
    ):
        service(
            trace,
            Repo(
                trace,
                result(
                    item
                ),
            ),
            None,
        ).deliver(
            policy=policy(),
            candidate=candidate(
                item
            ),
            decision_id="DEC-1",
            decided_at=NOW,
            consumer=lambda value: (
                trace.append(
                    "consumer"
                )
            ),
        )

    assert "commit" in trace
    assert "exit" in trace
    assert "resolve" in trace
    assert "consumer" not in trace


def test_corroboration_resolves_existing_revision_after_commit():
    item = revision()
    trace = []

    delivered = service(
        trace,
        Repo(
            trace,
            result(
                item,
                kind=(
                    MarketObservationDecisionKind
                    .CORROBORATED_EXISTING
                ),
                accepted=False,
            ),
        ),
        item,
    ).deliver(
        policy=policy(),
        candidate=candidate(
            item
        ),
        decision_id="DEC-1",
        decided_at=NOW,
        consumer=lambda value: (
            trace.append(
                "consumer"
            )
        ),
    )

    assert (
        delivered.revision
        == item
    )

    assert (
        trace.index("commit")
        < trace.index("exit")
        < trace.index("resolve")
        < trace.index("consumer")
    )
