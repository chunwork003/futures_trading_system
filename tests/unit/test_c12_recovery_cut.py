from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from persistence.account_authority import (
    AccountAuthorityCommitReceipt,
    AccountRecoveryCheckpoint,
    AccountStateHead,
)
from persistence.postgres.recovery import PostgresExecutionStateLoader
from persistence.recovery import ExecutionRestoreResult, ExecutionRestoreStatus, RecoveryCut
from trading.account import BrokerAccount

NOW=datetime(2026,9,27,tzinfo=timezone.utc)
ACCOUNT=BrokerAccount(broker="SINOPAC",account_ref="A")


def _closure():
    head=AccountStateHead(broker="SINOPAC",account_ref="A",current_revision=3,initialized=True)
    checkpoint=AccountRecoveryCheckpoint(broker="SINOPAC",account_ref="A",account_revision=3,expected_snapshot_id="S3",authority_commit_id="COMMIT-3",recorded_at=NOW)
    receipt=AccountAuthorityCommitReceipt(authority_commit_id="COMMIT-3",mutation_fingerprint="FP",broker="SINOPAC",account_ref="A",committed_revision=3,expected_snapshot_id="S3",recorded_at=NOW)
    return head,checkpoint,receipt


class Connection:
    def __init__(self,rows): self.rows=list(rows); self.statements=[]; self.commits=0; self.rollbacks=0
    def cursor(self):
        owner=self
        class Cursor:
            def __enter__(self): return self
            def __exit__(self,*args): return False
            def execute(self,sql,params=None): owner.statements.append((sql,params))
            def fetchone(self): return owner.rows.pop(0)
            def fetchall(self): return owner.rows.pop(0)
        return Cursor()


def _valid_rows():
    head,checkpoint,receipt=_closure()
    return [
        (head.broker,head.account_ref,head.current_revision,head.initialized,checkpoint.model_dump(mode="json"),receipt.model_dump(mode="json"),True),
        (4,9),
        (5,5),
        [("ATTEMPT-1",)],
    ]


def test_restore_status_and_result_invariants_are_explicit_and_immutable() -> None:
    assert [item.value for item in ExecutionRestoreStatus] == ["VALID","BASELINE_NOT_ESTABLISHED","RESTORE_FAILURE"]
    with pytest.raises(ValidationError,match="only VALID"):
        ExecutionRestoreResult(status=ExecutionRestoreStatus.VALID,cut=None,evidence=("partial",))
    result=ExecutionRestoreResult(status=ExecutionRestoreStatus.RESTORE_FAILURE,evidence=("missing closure",))
    with pytest.raises(ValidationError): result.status=ExecutionRestoreStatus.VALID


def test_recovery_cut_validates_exact_authority_closure_and_non_revision_witness() -> None:
    head,checkpoint,receipt=_closure()
    cut=RecoveryCut(account=ACCOUNT,head=head,checkpoint=checkpoint,receipt=receipt,recovery_generation=4,recovery_ingress_version=9,inbox_count=5,application_count=5,unresolved_broker_action_ids=("ATTEMPT-1",))
    assert cut.head.current_revision == 3 and cut.recovery_ingress_version == 9
    with pytest.raises(ValidationError,match="complete"):
        cut.model_copy(update={"recovery_ingress_version":None}).model_validate(cut.model_copy(update={"recovery_ingress_version":None}).model_dump())


def test_postgres_loader_uses_one_repeatable_read_boundary_and_returns_valid_cut() -> None:
    connection=Connection(_valid_rows())
    result=PostgresExecutionStateLoader(connection).load(ACCOUNT)
    assert result.status is ExecutionRestoreStatus.VALID
    assert result.cut is not None and result.cut.unresolved_broker_action_ids == ("ATTEMPT-1",)
    assert connection.statements[0][0] == "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"
    assert connection.commits == connection.rollbacks == 0


def test_missing_head_is_restore_failure_not_baseline_absence() -> None:
    result=PostgresExecutionStateLoader(Connection([None])).load(ACCOUNT)
    assert result.status is ExecutionRestoreStatus.RESTORE_FAILURE


def test_reserved_revision_zero_is_positive_baseline_not_established_proof() -> None:
    rows=[("SINOPAC","A",0,False,None,None,False)]
    result=PostgresExecutionStateLoader(Connection(rows)).load(ACCOUNT)
    assert result.status is ExecutionRestoreStatus.BASELINE_NOT_ESTABLISHED


@pytest.mark.parametrize("checkpoint,receipt,snapshot_exists",[(None,None,False),({},None,True),({}, {},False)])
def test_incomplete_closure_never_returns_valid(checkpoint,receipt,snapshot_exists) -> None:
    rows=[("SINOPAC","A",3,True,checkpoint,receipt,snapshot_exists)]
    result=PostgresExecutionStateLoader(Connection(rows)).load(ACCOUNT)
    assert result.status is ExecutionRestoreStatus.RESTORE_FAILURE and result.cut is None


def test_loader_has_no_broker_repair_or_account_mutation_surface() -> None:
    for name in ("submit","cancel","repair","advance_head","reanchor"):
        assert not hasattr(PostgresExecutionStateLoader,name)
