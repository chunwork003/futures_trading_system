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
    connection=Connection([("SINOPAC","A",4,3,0,True),("RUN-1",),(1,)])
    repo=PostgresReconciliationRunRepository(connection); repo.establish(boundary())
    assert "account_recovery_controls" in connection.statements[0][0]
    assert "INSERT INTO trading.reconciliation_runs" in connection.statements[1][0]
    assert not any("reconciliation_run_outcomes" in sql for sql,_ in connection.statements)
    assert connection.commits == connection.rollbacks == 0


def test_terminal_finalize_locks_boundary_and_identical_retry_is_idempotent() -> None:
    item=outcome()
    encoded=boundary().model_dump(mode="json")
    first=Connection([(encoded,),("SINOPAC","A",4,3,0,True),(encoded,),("RUN-1",),(1,)])
    PostgresReconciliationRunRepository(first).finalize(item)
    assert "FOR UPDATE" not in first.statements[0][0]
    assert "account_recovery_controls" in first.statements[1][0]
    assert "FOR UPDATE" in first.statements[2][0]
    retry=Connection([(encoded,),None,(encoded,),None,(item.model_dump(mode="json"),)])
    PostgresReconciliationRunRepository(retry).finalize(item)
    assert retry.commits == retry.rollbacks == 0


def test_conflicting_terminal_retry_fails_closed() -> None:
    different=outcome(evidence=("different",))
    existing=outcome().model_dump(mode="json")
    encoded=boundary().model_dump(mode="json")
    connection=Connection([(encoded,),None,(encoded,),None,(existing,)])
    with pytest.raises(ReconciliationCaseError,match="conflict"):
        PostgresReconciliationRunRepository(connection).finalize(different)


def test_run_audit_has_no_account_head_or_readiness_authority() -> None:
    for name in ("advance_head","ready","submit","repair"):
        assert not hasattr(PostgresReconciliationRunRepository,name)


def test_d1b_boundary_duplicate_does_not_advance_readiness() -> None:
    item=boundary(); encoded=item.model_dump(mode="json")
    connection=Connection([("SINOPAC","A",4,3,5,True),None,(encoded,)])
    PostgresReconciliationRunRepository(connection).establish(item)
    assert not any("readiness_revision=readiness_revision+1" in sql for sql,_ in connection.statements)


def test_d1b_finalize_rejects_boundary_change_before_outcome_insert() -> None:
    original=boundary(); changed=original.model_copy(update={"account":BrokerAccount(broker="SINOPAC",account_ref="B")})
    connection=Connection([(original.model_dump(mode="json"),),("SINOPAC","A",4,3,0,True),(changed.model_dump(mode="json"),)])
    with pytest.raises(ReconciliationCaseError,match="boundary"):
        PostgresReconciliationRunRepository(connection).finalize(outcome())
    assert not any("reconciliation_run_outcomes" in sql for sql,_ in connection.statements)


def test_d1b_boundary_conflict_and_inactive_control_never_advance() -> None:
    item=boundary(); different=item.model_copy(update={"recovery_cut_fingerprint":"OTHER"})
    conflict=Connection([("SINOPAC","A",4,3,5,True),None,(different.model_dump(mode="json"),)])
    with pytest.raises(ReconciliationCaseError,match="identity conflict"):
        PostgresReconciliationRunRepository(conflict).establish(item)
    assert not any("readiness_revision=readiness_revision+1" in sql for sql,_ in conflict.statements)
    inactive=Connection([None,("RUN-1",)])
    PostgresReconciliationRunRepository(inactive).establish(item)
    assert not any("readiness_revision=readiness_revision+1" in sql for sql,_ in inactive.statements)


def test_d1b_finalize_missing_boundary_fails_before_fence_or_outcome() -> None:
    connection=Connection([None])
    with pytest.raises(ReconciliationCaseError,match="boundary is missing"):
        PostgresReconciliationRunRepository(connection).finalize(outcome())
    assert len(connection.statements) == 1
    assert "FOR UPDATE" not in connection.statements[0][0]
    assert not any("account_recovery_controls" in sql or "reconciliation_run_outcomes" in sql for sql,_ in connection.statements)
