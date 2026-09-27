from datetime import datetime, timezone
import json

import pytest

from persistence.account_authority import AccountAuthorityCommitReceipt, AccountRecoveryCheckpoint, AccountStateHead
from persistence.postgres.recovery import PostgresAccountReadinessGate, StaleAccountReadinessError
from persistence.reconciliation import ReconciliationInputQualification, ReconciliationRunBoundary, ReconciliationRunOutcome, ReconciliationRunTechnicalOutcome
from persistence.recovery import (
    AccountReadinessEvidence,
    ExecutionRestoreResult,
    ExecutionRestoreStatus,
    RecoveryCut,
    RecoveryReadinessState,
    evaluate_account_readiness,
)
from trading.account import BrokerAccount
from trading.reconciliation import ReconciliationPolicy, ReconciliationResult, ReconciliationStatus

NOW=datetime(2026,9,27,tzinfo=timezone.utc)
ACCOUNT=BrokerAccount(broker="SINOPAC",account_ref="A")
REPORT_ROW=("IN-1",4,"PF",True,1,"APPLIED",5)
REPORT_WITNESS=json.dumps(REPORT_ROW,separators=(",",":"))


def restore(*,unresolved=()):
    head=AccountStateHead(broker="SINOPAC",account_ref="A",current_revision=3,initialized=True)
    checkpoint=AccountRecoveryCheckpoint(broker="SINOPAC",account_ref="A",account_revision=3,expected_snapshot_id="S3",authority_commit_id="AC3",recorded_at=NOW)
    receipt=AccountAuthorityCommitReceipt(authority_commit_id="AC3",mutation_fingerprint="FP",broker="SINOPAC",account_ref="A",committed_revision=3,expected_snapshot_id="S3",recorded_at=NOW)
    cut=RecoveryCut(account=ACCOUNT,head=head,checkpoint=checkpoint,receipt=receipt,recovery_generation=4,recovery_ingress_version=9,inbox_count=1,application_count=5,broker_report_witness=(REPORT_WITNESS,),current_nonterminal_order_anchors=(),unresolved_broker_action_ids=unresolved)
    return ExecutionRestoreResult(status=ExecutionRestoreStatus.VALID,cut=cut,evidence=("coherent cut",))


def run_outcome(*,status=ReconciliationStatus.MATCH,qualified=True):
    result=ReconciliationResult(status=status,expected=None,actual=None,evidence=("qualified evidence",) if status is ReconciliationStatus.UNKNOWN_EXTERNAL_STATE else ())
    return ReconciliationRunOutcome(run_id="RUN",technical_outcome=ReconciliationRunTechnicalOutcome.COMPLETED if qualified else ReconciliationRunTechnicalOutcome.EXTERNAL_STATE_UNKNOWN,input_qualification=ReconciliationInputQualification.QUALIFIED if qualified else ReconciliationInputQualification.UNQUALIFIED,results=(result,),finalized_at=NOW,evidence=("formal evaluation",))


def run_boundary(*,account=ACCOUNT,run_id="RUN",cut=None,policy=ReconciliationPolicy.STRICT_HALT):
    cut=cut or restore().cut
    assert cut is not None
    return ReconciliationRunBoundary(run_id=run_id,account=account,policy=policy,recovery_cut_fingerprint=cut.witness_fingerprint,account_revision=cut.head.current_revision,expected_snapshot_id=cut.checkpoint.expected_snapshot_id,authority_commit_id=cut.checkpoint.authority_commit_id,recovery_generation=cut.recovery_generation,recovery_ingress_version=cut.recovery_ingress_version,discovery_run_id="DISC-1",observation_id="OBS-1",established_at=NOW)


def evidence(**updates):
    restored=updates.get("restore_result",restore())
    values=dict(restore_result=restored,formal_run_boundary=run_boundary(cut=restored.cut) if restored.cut is not None else None,formal_run_outcome=run_outcome(),result_completeness_evidence=("complete broker and expected position collections",),discovery_complete=True,exact_correlation_integrity=True,continuity_current=True,pending_material_inbox=False,reconstruction_complete=True,reconstruction_conflict=False,mandatory_capabilities_available=True,out_of_horizon_unresolved_action=False)
    values.update(updates); return AccountReadinessEvidence(**values)


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


def test_all_positive_predicates_produce_ready() -> None:
    result=evaluate_account_readiness(account=ACCOUNT,evidence=evidence())
    assert result.state is RecoveryReadinessState.READY and result.reasons == ()


def test_a01_requested_account_must_match_recovery_cut_account() -> None:
    other=BrokerAccount(broker="SINOPAC",account_ref="B")
    assert evaluate_account_readiness(account=other,evidence=evidence()).state is RecoveryReadinessState.HALT


def test_a02_outcome_requires_matching_established_run_boundary() -> None:
    assert evaluate_account_readiness(account=ACCOUNT,evidence=evidence(formal_run_boundary=None)).state is RecoveryReadinessState.HALT
    assert evaluate_account_readiness(account=ACCOUNT,evidence=evidence(formal_run_boundary=run_boundary(run_id="OTHER"))).state is RecoveryReadinessState.HALT


def test_a03_historical_match_from_stale_cut_cannot_ready() -> None:
    stale=run_boundary().model_copy(update={"account_revision":2,"recovery_cut_fingerprint":"STALE"})
    assert evaluate_account_readiness(account=ACCOUNT,evidence=evidence(formal_run_boundary=stale)).state is RecoveryReadinessState.HALT
    stale_policy=run_boundary(policy=ReconciliationPolicy.MANUAL_REVIEW)
    assert evaluate_account_readiness(account=ACCOUNT,evidence=evidence(formal_run_boundary=stale_policy)).state is RecoveryReadinessState.HALT
    missing_discovery=run_boundary().model_copy(update={"discovery_run_id":None})
    assert evaluate_account_readiness(account=ACCOUNT,evidence=evidence(formal_run_boundary=missing_discovery)).state is RecoveryReadinessState.HALT


def test_a04_empty_results_require_positive_completeness_evidence() -> None:
    empty=run_outcome().model_copy(update={"results":()})
    assert evaluate_account_readiness(account=ACCOUNT,evidence=evidence(formal_run_outcome=empty,result_completeness_evidence=())).state is not RecoveryReadinessState.READY


@pytest.mark.parametrize("updates",[
    {"mandatory_capabilities_available":False},
    {"exact_correlation_integrity":False},
    {"reconstruction_conflict":True},
    {"formal_run_outcome":None},
])
def test_integrity_authority_or_required_run_failure_halts(updates) -> None:
    assert evaluate_account_readiness(account=ACCOUNT,evidence=evidence(**updates)).state is RecoveryReadinessState.HALT


@pytest.mark.parametrize("updates",[
    {"discovery_complete":False},
    {"continuity_current":False},
    {"pending_material_inbox":True},
    {"reconstruction_complete":False},
    {"out_of_horizon_unresolved_action":True},
    {"formal_run_outcome":run_outcome(status=ReconciliationStatus.UNKNOWN_EXTERNAL_STATE,qualified=False)},
])
def test_unknown_degraded_or_incomplete_evidence_requires_review(updates) -> None:
    assert evaluate_account_readiness(account=ACCOUNT,evidence=evidence(**updates)).state is RecoveryReadinessState.REVIEW


def test_unresolved_broker_action_blocks_ready_and_halt_precedes_review() -> None:
    assert evaluate_account_readiness(account=ACCOUNT,evidence=evidence(restore_result=restore(unresolved=("ATTEMPT",)))).state is RecoveryReadinessState.REVIEW
    result=evaluate_account_readiness(account=ACCOUNT,evidence=evidence(restore_result=restore(unresolved=("ATTEMPT",)),mandatory_capabilities_available=False))
    assert result.state is RecoveryReadinessState.HALT


def test_invalid_cut_halts_without_position_or_strategy_shortcut() -> None:
    invalid=ExecutionRestoreResult(status=ExecutionRestoreStatus.RESTORE_FAILURE,evidence=("missing",))
    assert evaluate_account_readiness(account=ACCOUNT,evidence=evidence(restore_result=invalid)).state is RecoveryReadinessState.HALT


def test_final_local_revalidation_accepts_exact_witness_without_mutation() -> None:
    evaluation=evaluate_account_readiness(account=ACCOUNT,evidence=evidence())
    connection=Connection([(3,),(4,9,True),[REPORT_ROW],[],[]])
    PostgresAccountReadinessGate(connection).revalidate(evaluation)
    assert connection.commits == connection.rollbacks == 0
    assert any("FOR SHARE" in sql for sql,_ in connection.statements)


def test_changed_revision_or_non_revision_witness_requires_reevaluation() -> None:
    evaluation=evaluate_account_readiness(account=ACCOUNT,evidence=evidence())
    for rows in (
        [(4,),(4,9,True),[REPORT_ROW],[],[]],
        [(3,),(4,10,True),[REPORT_ROW],[],[]],
        [(3,),(4,9,True),[("IN-2",4,"PF",True,1,"APPLIED",5)],[],[]],
        [(3,),(4,9,True),[REPORT_ROW],[("ORDER-1",2,"SUBMITTED",{},0,1)],[]],
        [(3,),(4,9,True),[REPORT_ROW],[],[("ATTEMPT",)]],
    ):
        with pytest.raises(StaleAccountReadinessError,match="reevaluation"):
            PostgresAccountReadinessGate(Connection(rows)).revalidate(evaluation)


def test_readiness_gate_has_no_broker_or_economic_mutation_surface() -> None:
    for name in ("submit","cancel","list_positions","advance_head","repair"):
        assert not hasattr(PostgresAccountReadinessGate,name)
