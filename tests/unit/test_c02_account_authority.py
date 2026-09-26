from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from persistence.account_authority import (
    AccountAuthorityCommitReceipt,
    AccountAuthorityConflictError,
    AccountAuthorityIntegrityError,
    AccountRecoveryCheckpoint,
    AccountStateHead,
    validate_authority_closure,
)
from persistence.postgres.account_authority import PostgresAccountAuthorityRepository


NOW = datetime(2026, 9, 26, tzinfo=timezone.utc)


def _closure():
    head = AccountStateHead(broker="sinopac", account_ref=" A ", current_revision=1, initialized=True)
    checkpoint = AccountRecoveryCheckpoint(
        broker="SINOPAC", account_ref="A", account_revision=1,
        expected_snapshot_id="SNAP-1", authority_commit_id="COMMIT-1", recorded_at=NOW,
    )
    receipt = AccountAuthorityCommitReceipt(
        authority_commit_id="COMMIT-1", mutation_fingerprint="FP-1", broker="SINOPAC",
        account_ref="A", committed_revision=1, expected_snapshot_id="SNAP-1", recorded_at=NOW,
    )
    return head, checkpoint, receipt


def test_models_are_immutable_and_revision_zero_is_positive_not_initialized() -> None:
    control = AccountStateHead(broker="SINOPAC", account_ref="A", current_revision=0, initialized=False)
    with pytest.raises(ValidationError):
        control.current_revision = 1
    with pytest.raises(ValidationError, match="revision"):
        AccountStateHead(broker="SINOPAC", account_ref="A", current_revision=1, initialized=False)


def test_exact_authority_closure_and_no_latest_substitution() -> None:
    head, checkpoint, receipt = _closure()
    validate_authority_closure(head=head, checkpoint=checkpoint, receipt=receipt)
    with pytest.raises(AccountAuthorityIntegrityError, match="exact expected snapshot"):
        validate_authority_closure(
            head=head,
            checkpoint=checkpoint,
            receipt=receipt.model_copy(update={"expected_snapshot_id": "NEWER"}),
        )


class _Cursor:
    def __init__(self, connection): self.connection = connection
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def execute(self, sql, params=None): self.connection.calls.append((sql, params))
    def fetchone(self): return self.connection.rows.pop(0) if self.connection.rows else None


class _Connection:
    def __init__(self, rows=()): self.rows=list(rows); self.calls=[]; self.commits=0
    def cursor(self): return _Cursor(self)
    def commit(self): self.commits += 1


def test_postgres_head_lock_and_contiguous_advance_without_repository_commit() -> None:
    connection = _Connection(rows=[("SINOPAC", "A", 1, True), (2,)])
    repository = PostgresAccountAuthorityRepository(connection)
    head = repository.lock_head("sinopac", "A")
    assert head.current_revision == 1
    assert "FOR UPDATE" in connection.calls[0][0]
    repository.advance_head(head.model_copy(update={"current_revision": 2}), expected_revision=1)
    assert connection.commits == 0
    with pytest.raises(AccountAuthorityConflictError, match="contiguously"):
        repository.advance_head(head.model_copy(update={"current_revision": 3}), expected_revision=1)


def test_0005_has_exact_checkpoint_and_non_destructive_authority_schema() -> None:
    sql = Path("persistence/postgres/migrations/0005_account_authority.sql").read_text(encoding="utf-8")
    for table in ("account_state_heads", "account_recovery_checkpoints", "account_authority_commit_receipts"):
        assert f"CREATE TABLE trading.{table}" in sql
        assert f"COMMENT ON TABLE trading.{table}" in sql
    assert "expected_snapshot_id" in sql
    assert "TIMESTAMPTZ" in sql and "JSONB" in sql and "FOREIGN KEY" in sql
    assert "DROP " not in sql and "UPDATE " not in sql and "DELETE " not in sql
