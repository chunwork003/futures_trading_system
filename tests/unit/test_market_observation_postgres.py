from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

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
    MarketObservationRoutingRole,
    MarketObservationSourcePolicyRule,
    evaluate_market_observation_candidate,
)
from persistence.market_observation import (
    MarketObservationIdentityConflictError,
)
from persistence.postgres.market_observation import (
    PostgresMarketObservationAcceptanceRepository,
    classify_market_observation_revision_collision,
)


NOW = datetime(
    2026,
    9,
    26,
    2,
    0,
    tzinfo=timezone.utc,
)


def _policy():
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


def _candidate():
    key = canonicalize_market_observation_logical_key(
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

    content = canonicalize_market_observation_content(
        open="20000",
        high="20050",
        low="19980",
        close="20030",
        volume=100,
        amount="2003000",
        trade_count=50,
        tick_count=None,
        trade_date=date(2026, 9, 26),
        session_ref="DAY",
    )

    fingerprint = content.content_fingerprint

    revision_id = build_market_observation_revision_id(
        logical_key=key,
        content_fingerprint=fingerprint,
    )

    return MarketObservationCandidateEvidence(
        candidate_id="CAND-1",
        logical_key=key,
        content=content,
        content_fingerprint=fingerprint,
        observation_revision_id=revision_id,
        source_id="SRC-A",
        routing_role=MarketObservationRoutingRole.PRIMARY,
        source_record_ref="ROW-1",
        formal_correction_ref=None,
        received_at=NOW,
        provenance_json={"fixture": True},
        acceptance_policy_id="POL-1",
        acceptance_policy_version=1,
        acceptance_scope_ref="TXF-1M",
    )


def _initial_revision():
    plan = evaluate_market_observation_candidate(
        policy=_policy(),
        candidate=_candidate(),
        current_revision=None,
        accepted_at=NOW,
    )

    assert plan.accepted_revision is not None

    return plan.accepted_revision


class ScriptedCursor:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql, params=None):
        self.connection.executed.append(
            (
                " ".join(sql.split()),
                params,
            )
        )

    def fetchone(self):
        if not self.connection.fetchone_results:
            return None

        return self.connection.fetchone_results.pop(0)


class ScriptedConnection:
    def __init__(self, fetchone_results):
        self.fetchone_results = list(fetchone_results)
        self.executed = []
        self.commits = 0
        self.rollbacks = 0

    def cursor(self):
        return ScriptedCursor(self)

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def test_migration_is_exactly_new_version_0003() -> None:
    path = Path(
        "persistence/postgres/migrations/"
        "0003_market_observation_evidence.sql"
    )

    assert path.exists()

    migrations = sorted(
        item.name
        for item in path.parent.glob("*.sql")
    )

    assert "0001_event_ledger.sql" in migrations
    assert "0002_operational_persistence.sql" in migrations
    assert "0003_market_observation_evidence.sql" in migrations


def test_migration_contains_required_operational_tables() -> None:
    sql = Path(
        "persistence/postgres/migrations/"
        "0003_market_observation_evidence.sql"
    ).read_text(encoding="utf-8")

    tables = (
        "market_observation_acceptance_policies",
        "market_observation_candidates",
        "market_observation_revisions",
        "market_observation_candidate_decisions",
        "market_observation_revision_evidence",
        "market_observation_heads",
    )

    for table in tables:
        assert f"CREATE TABLE trading.{table}" in sql
        assert f"COMMENT ON TABLE trading.{table}" in sql


def test_migration_enforces_atomic_identity_and_revision_uniqueness() -> None:
    sql = Path(
        "persistence/postgres/migrations/"
        "0003_market_observation_evidence.sql"
    ).read_text(encoding="utf-8")

    assert (
        "observation_revision_id TEXT PRIMARY KEY"
        in sql
    )
    assert (
        "CONSTRAINT uq_market_observation_revision_content"
        in sql
    )
    assert (
        "CONSTRAINT uq_market_observation_revision_seq"
        in sql
    )
    assert (
        "CONSTRAINT uq_market_observation_logical_head"
        in sql
    )
    assert sql.count("UNIQUE NULLS NOT DISTINCT") >= 3


def test_nullable_contract_id_is_part_of_nulls_not_distinct_uniqueness() -> None:
    sql = Path(
        "persistence/postgres/migrations/"
        "0003_market_observation_evidence.sql"
    ).read_text(encoding="utf-8")

    assert "UNIQUE NULLS NOT DISTINCT" in sql
    assert "contract_id" in sql


def test_migration_has_required_types_constraints_and_chinese_comments() -> None:
    sql = Path(
        "persistence/postgres/migrations/"
        "0003_market_observation_evidence.sql"
    ).read_text(encoding="utf-8")

    for token in (
        "NUMERIC",
        "TIMESTAMPTZ",
        "JSONB",
        "PRIMARY KEY",
        "FOREIGN KEY",
        "CHECK",
        "COMMENT ON TABLE",
        "COMMENT ON COLUMN",
    ):
        assert token in sql

    for chinese_text in (
        "不可變",
        "候選",
        "接受",
        "修訂",
        "隔離",
    ):
        assert chinese_text in sql


def test_migration_does_not_rewrite_historical_schema() -> None:
    sql = Path(
        "persistence/postgres/migrations/"
        "0003_market_observation_evidence.sql"
    ).read_text(encoding="utf-8")

    assert "ALTER TABLE trading.orders" not in sql
    assert "ALTER TABLE trading.strategy_state_snapshots" not in sql
    assert "DROP TABLE" not in sql
    assert "DELETE FROM" not in sql


def test_repository_uses_database_atomic_insert_and_head_lock() -> None:
    source = Path(
        "persistence/postgres/market_observation.py"
    ).read_text(encoding="utf-8")

    assert "ON CONFLICT DO NOTHING" in source
    assert "RETURNING" in source
    assert "FOR UPDATE" in source
    assert (
        "contract_id IS NOT DISTINCT FROM %s"
        in source
    )


def test_repository_never_commits_or_rolls_back() -> None:
    source = Path(
        "persistence/postgres/market_observation.py"
    ).read_text(encoding="utf-8")

    assert ".commit(" not in source
    assert ".rollback(" not in source


def test_repository_does_not_update_immutable_history_tables() -> None:
    source = Path(
        "persistence/postgres/market_observation.py"
    ).read_text(encoding="utf-8")

    forbidden = (
        "UPDATE trading.market_observation_candidates",
        "UPDATE trading.market_observation_revisions",
        "UPDATE trading.market_observation_candidate_decisions",
        "UPDATE trading.market_observation_revision_evidence",
        "DELETE FROM trading.market_observation_",
    )

    for token in forbidden:
        assert token not in source

    assert "UPDATE trading.market_observation_heads" in source


def test_repository_has_no_select_if_missing_insert_uniqueness_authority() -> None:
    source = Path(
        "persistence/postgres/market_observation.py"
    ).read_text(encoding="utf-8")

    assert "ON CONFLICT DO NOTHING" in source
    assert "FOR UPDATE" in source


def test_exact_revision_collision_is_idempotent_duplicate() -> None:
    revision = _initial_revision()

    signature = (
        revision.observation_revision_id.value,
        revision.logical_key.instrument_id,
        revision.logical_key.contract_id,
        revision.logical_key.timeframe,
        revision.logical_key.interval_start_at,
        1,
        revision.content.open,
        revision.content.high,
        revision.content.low,
        revision.content.close,
        revision.content.volume,
        revision.content.amount,
        revision.content.trade_count,
        revision.content.tick_count,
        revision.content.trade_date,
        revision.content.session_ref,
        revision.content_fingerprint.value,
        revision.revision_seq,
        None,
        revision.accepted_at,
        revision.acceptance_policy_id,
        revision.acceptance_policy_version,
        revision.acceptance_scope_ref,
    )

    assert (
        classify_market_observation_revision_collision(
            persisted_signature=signature,
            attempted_revision=revision,
        )
        is False
    )


def test_different_revision_evidence_under_same_identity_is_typed_conflict() -> None:
    revision = _initial_revision()

    bad_signature = (
        revision.observation_revision_id.value,
        revision.logical_key.instrument_id,
        revision.logical_key.contract_id,
        revision.logical_key.timeframe,
        revision.logical_key.interval_start_at,
        1,
        revision.content.open,
        revision.content.high,
        revision.content.low,
        Decimal("99999"),
        revision.content.volume,
        revision.content.amount,
        revision.content.trade_count,
        revision.content.tick_count,
        revision.content.trade_date,
        revision.content.session_ref,
        revision.content_fingerprint.value,
        revision.revision_seq,
        None,
        revision.accepted_at,
        revision.acceptance_policy_id,
        revision.acceptance_policy_version,
        revision.acceptance_scope_ref,
    )

    with pytest.raises(
        MarketObservationIdentityConflictError
    ):
        classify_market_observation_revision_collision(
            persisted_signature=bad_signature,
            attempted_revision=revision,
        )


def test_uniqueness_collision_without_revision_id_match_is_typed_conflict() -> None:
    revision = _initial_revision()

    with pytest.raises(
        MarketObservationIdentityConflictError,
        match="without an exact",
    ):
        classify_market_observation_revision_collision(
            persisted_signature=None,
            attempted_revision=revision,
        )


def test_initial_candidate_process_is_atomic_repository_sequence_without_commit() -> None:
    candidate = _candidate()
    policy = _policy()

    connection = ScriptedConnection(
        [
            ("POL-1",),   # policy INSERT RETURNING
            (1,),         # head INSERT RETURNING
            (1, None, 0, False, None),  # head SELECT FOR UPDATE
            ("CAND-1",),  # candidate INSERT RETURNING
            (
                candidate.observation_revision_id.value,
            ),            # revision INSERT RETURNING
            ("DEC-1",),   # decision INSERT RETURNING
        ]
    )

    repository = PostgresMarketObservationAcceptanceRepository(
        connection
    )

    result = repository.process_candidate(
        policy=policy,
        candidate=candidate,
        decision_id="DEC-1",
        decided_at=NOW,
    )

    assert (
        result.decision.decision_kind
        is MarketObservationDecisionKind.ACCEPTED_NEW_REVISION
    )
    assert result.accepted_revision is not None
    assert result.current_revision_seq == 1
    assert result.current_revision_id == (
        candidate.observation_revision_id
    )
    assert not result.quarantined
    assert connection.commits == 0
    assert connection.rollbacks == 0

    sql = "\n".join(
        item[0]
        for item in connection.executed
    )

    assert "ON CONFLICT DO NOTHING" in sql
    assert "FOR UPDATE" in sql
    assert (
        "INSERT INTO trading.market_observation_candidates"
        in sql
    )
    assert (
        "INSERT INTO trading.market_observation_revisions"
        in sql
    )
    assert (
        "INSERT INTO trading.market_observation_candidate_decisions"
        in sql
    )
    assert (
        "INSERT INTO trading.market_observation_revision_evidence"
        in sql
    )
    assert (
        "UPDATE trading.market_observation_heads"
        in sql
    )


def test_repository_source_contains_no_manual_force_accept_bypass() -> None:
    source = Path(
        "persistence/postgres/market_observation.py"
    ).read_text(encoding="utf-8")

    for token in (
        "force_accept",
        "ignore_quarantine",
        "actor == ",
        "reason == ",
    ):
        assert token not in source


def test_c24_does_not_modify_strategy_delivery_contract() -> None:
    source = Path(
        "persistence/postgres/market_observation.py"
    ).read_text(encoding="utf-8")

    assert "StrategyStateSnapshot" not in source
    assert "ExecutionTriggerRef" not in source
    assert "last_market_observation_id" not in source


def test_c24_does_not_claim_r14_completeness_or_k520() -> None:
    source = Path(
        "persistence/postgres/market_observation.py"
    ).read_text(encoding="utf-8")

    assert "K520" not in source
    assert "gap detection" not in source.lower()
    assert "no candidate == legitimate" not in source.lower()
