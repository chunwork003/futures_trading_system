from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from persistence.postgres.reconciliation import PostgresReconciliationRunRepository
from persistence.reconciliation import (
    ReconciliationInputQualification,
    ReconciliationRunBoundary,
    ReconciliationRunOutcome,
    ReconciliationRunTechnicalOutcome,
)
from trading.account import BrokerAccount
from trading.reconciliation import (
    ReconciliationCaseError,
    ReconciliationPolicy,
    ReconciliationResult,
    ReconciliationStatus,
)

NOW=datetime(2026,9,27,tzinfo=timezone.utc)
ACCOUNT=BrokerAccount(broker="SINOPAC",account_ref="A")


def boundary():
    return ReconciliationRunBoundary(run_id="RUN-1",account=ACCOUNT,policy=ReconciliationPolicy.STRICT_HALT,recovery_cut_fingerprint="CUT-FP",account_revision=3,expected_snapshot_id="S3",authority_commit_id="COMMIT-3",recovery_generation=4,recovery_ingress_version=9,discovery_run_id="DISC-1",observation_id="OBS-1",established_at=NOW)


def match_result():
    return ReconciliationResult(status=ReconciliationStatus.MATCH,expected=None,actual=None)


def outcome(**updates):
    values=dict(run_id="RUN-1",technical_outcome=ReconciliationRunTechnicalOutcome.COMPLETED,input_qualification=ReconciliationInputQualification.QUALIFIED,results=(match_result(),),finalized_at=NOW,evidence=("exact evaluated world",))
    values.update(updates); return ReconciliationRunOutcome(**values)


class Connection:
    def __init__(self,rows): self.rows=list(rows); self.statements=[]; self.commits=0; self.rollbacks=0
    def cursor(self):
        owner=self
        class Cursor:
            def __enter__(self): return self
            def __exit__(self,*args): return False
            def execute(self,sql,params=None): owner.statements.append((sql,params))
            def fetchone(self): return owner.rows.pop(0)
        return Cursor()


def test_run_boundary_is_account_scoped_immutable_and_currentness_complete() -> None:
    item=boundary()
    assert item.account == ACCOUNT and item.recovery_ingress_version == 9
    with pytest.raises(ValidationError): item.account=BrokerAccount(broker="SINOPAC",account_ref="B")
    with pytest.raises(ValidationError,match="complete"):
        ReconciliationRunBoundary(**{**item.model_dump(),"recovery_ingress_version":None})


def test_technical_input_and_domain_axes_are_separate() -> None:
    assert outcome().technical_outcome is ReconciliationRunTechnicalOutcome.COMPLETED
    with pytest.raises(ValidationError,match="cannot produce MATCH"):
        outcome(input_qualification=ReconciliationInputQualification.UNQUALIFIED)
    unknown=ReconciliationResult(status=ReconciliationStatus.UNKNOWN_EXTERNAL_STATE,expected=None,actual=None,evidence=("qualified provider failure",))
    item=outcome(technical_outcome=ReconciliationRunTechnicalOutcome.EXTERNAL_STATE_UNKNOWN,input_qualification=ReconciliationInputQualification.UNQUALIFIED,results=(unknown,))
    assert item.results[0].status is ReconciliationStatus.UNKNOWN_EXTERNAL_STATE


def test_run_boundary_is_durable_before_terminal_and_crash_is_detectable() -> None:
    connection=Connection([("RUN-1",)])
    repo=PostgresReconciliationRunRepository(connection); repo.establish(boundary())
    assert "INSERT INTO trading.reconciliation_runs" in connection.statements[0][0]
    assert not any("reconciliation_run_outcomes" in sql for sql,_ in connection.statements)
    assert connection.commits == connection.rollbacks == 0


def test_terminal_finalize_locks_boundary_and_identical_retry_is_idempotent() -> None:
    item=outcome()
    first=Connection([("boundary",),("RUN-1",)])
    PostgresReconciliationRunRepository(first).finalize(item)
    assert "FOR UPDATE" in first.statements[0][0]
    retry=Connection([("boundary",),None,(item.model_dump(mode="json"),)])
    PostgresReconciliationRunRepository(retry).finalize(item)
    assert retry.commits == retry.rollbacks == 0


def test_conflicting_terminal_retry_fails_closed() -> None:
    different=outcome(evidence=("different",))
    existing=outcome().model_dump(mode="json")
    connection=Connection([("boundary",),None,(existing,)])
    with pytest.raises(ReconciliationCaseError,match="conflict"):
        PostgresReconciliationRunRepository(connection).finalize(different)


def test_run_audit_has_no_account_head_or_readiness_authority() -> None:
    for name in ("advance_head","ready","submit","repair"):
        assert not hasattr(PostgresReconciliationRunRepository,name)
