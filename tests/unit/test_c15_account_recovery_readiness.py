from datetime import datetime, timezone, timedelta
from decimal import Decimal
import json

import pytest

from persistence.account_authority import AccountAuthorityCommitReceipt, AccountRecoveryCheckpoint, AccountStateHead
from persistence.postgres.recovery import PostgresAccountReadinessGate, StaleAccountReadinessError
from persistence.reconciliation import ReconciliationInputQualification, ReconciliationRunBoundary, ReconciliationRunOutcome, ReconciliationRunTechnicalOutcome
from persistence.recovery import (
    AccountReadinessEvidence,
    CapabilityReadinessEvidence,
    ExecutionRestoreResult,
    ExecutionRestoreStatus,
    RecoveryCut,
    RecoveryReadinessState,
    ReconciliationCompletenessEvidence,
    ReconstructionReadinessEvidence,
    TrustedRecoveryEvidenceError,
    TrustedRecoveryEvidenceResolver,
    evaluate_account_readiness,
)
from persistence.broker_recovery import ExecutionContinuityEpoch
from persistence.broker_recovery import BrokerDiscoveryReceipt, BrokerReconstructionReceipt
from persistence.account import AccountPositionSnapshot, BrokerPositionObservation
from adapters.capabilities import BrokerCapability, BrokerVerificationMode, StaticBrokerCapabilityProvider
from adapters.sinopac.capabilities import SINOPAC_CAPABILITY_REGISTRY_SNAPSHOT
from trading.broker_recovery import BrokerDealSetCompleteness, BrokerReconstructionPlan
from trading.execution import Fill, OrderStatus
from trading.broker_recovery import BrokerDiscoveryIntegrity, BrokerDiscoveryResult, DiscoveryCompleteness, ExactMatchCardinality
from trading.account import BrokerAccount
from trading.reconciliation import ReconciliationPolicy, ReconciliationResult, ReconciliationStatus

NOW=datetime(2026,9,27,tzinfo=timezone.utc)
ACCOUNT=BrokerAccount(broker="SINOPAC",account_ref="A")
REPORT_ROW=("IN-1",4,"PF",True,1,"APPLIED",5)
REPORT_WITNESS=json.dumps(REPORT_ROW,separators=(",",":"))
CONTINUITY_ROW=("EPOCH-1","SINOPAC","A",4,True,False,NOW,{"evidence":["current"]})
CONTINUITY_WITNESS=json.dumps(CONTINUITY_ROW,separators=(",",":"),default=str)


def restore(*,unresolved=()):
    head=AccountStateHead(broker="SINOPAC",account_ref="A",current_revision=3,initialized=True)
    checkpoint=AccountRecoveryCheckpoint(broker="SINOPAC",account_ref="A",account_revision=3,expected_snapshot_id="S3",authority_commit_id="AC3",recorded_at=NOW)
    receipt=AccountAuthorityCommitReceipt(authority_commit_id="AC3",mutation_fingerprint="FP",broker="SINOPAC",account_ref="A",committed_revision=3,expected_snapshot_id="S3",recorded_at=NOW)
    cut=RecoveryCut(account=ACCOUNT,head=head,checkpoint=checkpoint,receipt=receipt,recovery_generation=4,recovery_ingress_version=9,inbox_count=1,application_count=5,broker_report_witness=(REPORT_WITNESS,),current_nonterminal_order_anchors=(),continuity_epoch_witness=(CONTINUITY_WITNESS,),unresolved_broker_action_ids=unresolved)
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
    cut=restored.cut
    boundary=run_boundary(cut=cut) if cut is not None else None
    discovery=BrokerDiscoveryResult(discovery_run_id="DISC-1",account=ACCOUNT,required_scope="ORDERS",horizon_start=NOW,horizon_end=NOW,refreshed_at=NOW,completeness=DiscoveryCompleteness.COMPLETE,exact_matches=(),cardinality=ExactMatchCardinality.ZERO,integrity=BrokerDiscoveryIntegrity.CONSISTENT,evidence=("complete scope",)) if cut is not None else None
    continuity=ExecutionContinuityEpoch(epoch_id="EPOCH-1",broker=ACCOUNT.broker,account_ref=ACCOUNT.account_ref,generation=4,trusted_current=True,historical_degradation=False,anchored_at=NOW,evidence=("current",)) if cut is not None else None
    completeness=ReconciliationCompletenessEvidence(evidence_id="COMPLETE-1",account=ACCOUNT,run_id="RUN",recovery_cut_fingerprint=cut.witness_fingerprint,expected_complete=True,actual_complete=True) if cut is not None else None
    reconstruction=ReconstructionReadinessEvidence(evidence_id="RECON-1",account=ACCOUNT,recovery_cut_fingerprint=cut.witness_fingerprint,discovery_run_id="DISC-1",complete=True,conflict=False) if cut is not None else None
    capability=CapabilityReadinessEvidence(evidence_id="CAP-1",account=ACCOUNT,recovery_cut_fingerprint=cut.witness_fingerprint,source_refs=("BROKER-CAPABILITY-MATRIX",),available=True) if cut is not None else None
    values=dict(restore_result=restored,formal_run_boundary=boundary,formal_run_outcome=run_outcome(),discovery_result=discovery,continuity_epoch=continuity,result_completeness=completeness,reconstruction_evidence=reconstruction,capability_evidence=capability,discovery_complete=True,exact_correlation_integrity=True,continuity_current=True,pending_material_inbox=False,reconstruction_complete=True,reconstruction_conflict=False,mandatory_capabilities_available=True,out_of_horizon_unresolved_action=False)
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
    assert evaluate_account_readiness(account=ACCOUNT,evidence=evidence(formal_run_outcome=empty,result_completeness=None)).state is not RecoveryReadinessState.READY


def test_rf02_positive_booleans_or_arbitrary_strings_cannot_authorize_ready() -> None:
    item=evidence(discovery_result=None,continuity_epoch=None,result_completeness=None,reconstruction_evidence=None,capability_evidence=None)
    assert evaluate_account_readiness(account=ACCOUNT,evidence=item).state is not RecoveryReadinessState.READY


def test_rf02_typed_evidence_must_bind_account_run_generation_and_cut() -> None:
    base=evidence()
    other=BrokerAccount(broker="SINOPAC",account_ref="B")
    wrong_discovery=base.discovery_result.model_copy(update={"account":other})
    wrong_continuity=base.continuity_epoch.model_copy(update={"generation":5})
    wrong_reconstruction=base.reconstruction_evidence.model_copy(update={"recovery_cut_fingerprint":"OTHER"})
    wrong_capability=base.capability_evidence.model_copy(update={"account":other})
    for updates in ({"discovery_result":wrong_discovery},{"continuity_epoch":wrong_continuity},{"reconstruction_evidence":wrong_reconstruction},{"capability_evidence":wrong_capability}):
        assert evaluate_account_readiness(account=ACCOUNT,evidence=evidence(**updates)).state is not RecoveryReadinessState.READY


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
    boundary=evidence().formal_run_boundary
    outcome=evidence().formal_run_outcome
    connection=Connection([(3,),(4,9,True),[REPORT_ROW],[],[],[],[CONTINUITY_ROW],[],[],[],(boundary.model_dump(mode="json"),outcome.model_dump(mode="json"))])
    PostgresAccountReadinessGate(connection).revalidate(evaluation)
    assert connection.commits == connection.rollbacks == 0
    assert any("FOR SHARE" in sql for sql,_ in connection.statements)


def test_changed_revision_or_non_revision_witness_requires_reevaluation() -> None:
    evaluation=evaluate_account_readiness(account=ACCOUNT,evidence=evidence())
    for rows in (
        [(4,),(4,9,True),[REPORT_ROW],[],[],[],[CONTINUITY_ROW],[],[],[],None],
        [(3,),(4,10,True),[REPORT_ROW],[],[],[],[CONTINUITY_ROW],[],[],[],None],
        [(3,),(4,9,True),[("IN-2",4,"PF",True,1,"APPLIED",5)],[],[],[],[CONTINUITY_ROW],[],[],[],None],
        [(3,),(4,9,True),[REPORT_ROW],[("ORDER-1",2,"SUBMITTED",{})],[],[],[CONTINUITY_ROW],[],[],[],None],
        [(3,),(4,9,True),[REPORT_ROW],[],[],[],[("EPOCH-2","SINOPAC","A",4,True,False,NOW,{})],[],[],[],None],
        [(3,),(4,9,True),[REPORT_ROW],[],[],[],[CONTINUITY_ROW],[],[],[("ATTEMPT",)],None],
    ):
        with pytest.raises(StaleAccountReadinessError,match="reevaluation"):
            PostgresAccountReadinessGate(Connection(rows)).revalidate(evaluation)


def test_readiness_gate_has_no_broker_or_economic_mutation_surface() -> None:
    for name in ("submit","cancel","list_positions","advance_head","repair"):
        assert not hasattr(PostgresAccountReadinessGate,name)


def _trusted_resolver_fixture():
    discovery_result=BrokerDiscoveryResult(discovery_run_id="DISC-1",account=ACCOUNT,required_scope="ORDERS",horizon_start=NOW,horizon_end=NOW,refreshed_at=NOW,completeness=DiscoveryCompleteness.COMPLETE,exact_matches=(),cardinality=ExactMatchCardinality.ZERO,integrity=BrokerDiscoveryIntegrity.CONSISTENT,evidence=("complete",))
    discovery=BrokerDiscoveryReceipt(discovery_run_id="DISC-1",account=ACCOUNT,generation=4,result=discovery_result,producer_id="RECOVERY",contract_version="V1",recorded_at=NOW)
    plan=BrokerReconstructionPlan(status=OrderStatus.PENDING,accepted_fills=(),filled_quantity=0,average_fill_price=None,material_change=False)
    reconstruction=BrokerReconstructionReceipt(reconstruction_receipt_id="RECON-1",account=ACCOUNT,generation=4,recovery_cut_fingerprint="CUT",discovery_run_id="DISC-1",order_id="ORDER-1",broker_deals=(),local_fill_ids=(),lifecycle_evidence=None,plan=plan,deal_set_completeness=BrokerDealSetCompleteness.COMPLETE,producer_id="RECOVERY",contract_version="V1",recorded_at=NOW)
    expected=AccountPositionSnapshot(snapshot_id="SNAP-1",broker="SINOPAC",account_ref="A",effective_at=NOW,recorded_at=NOW,source_event_id="EVENT",positions=())
    actual=BrokerPositionObservation(observation_id="OBS-1",broker="SINOPAC",account_ref="A",observed_at=NOW,recorded_at=NOW,positions=())
    class RecoveryRepo:
        def get_discovery_receipt(self,*,discovery_run_id,account): return discovery if discovery_run_id=="DISC-1" else None
        def get_reconstruction_receipt(self,*,reconstruction_receipt_id,account): return reconstruction if reconstruction_receipt_id=="RECON-1" else None
    class ExactRepo:
        def __init__(self,item,key): self.item,self.key=item,key
        def get_exact(self,**kwargs): return self.item if self.key in kwargs.values() else None
    resolver=TrustedRecoveryEvidenceResolver(broker_recovery_repository=RecoveryRepo(),expected_snapshot_repository=ExactRepo(expected,"SNAP-1"),broker_observation_repository=ExactRepo(actual,"OBS-1"),capability_provider=StaticBrokerCapabilityProvider((SINOPAC_CAPABILITY_REGISTRY_SNAPSHOT,)))
    return resolver,discovery,reconstruction


def test_trusted_resolver_re_reads_exact_authority_without_making_ready() -> None:
    resolver,discovery,reconstruction= _trusted_resolver_fixture()
    core=resolver.resolve(account=ACCOUNT,recovery_generation=4,recovery_cut_fingerprint="CUT",discovery_run_id="DISC-1",reconstruction_receipt_ids=("RECON-1",),expected_snapshot_id="SNAP-1",broker_observation_id="OBS-1",required_capabilities=(BrokerCapability.ACCOUNT_QUERY,),required_verification_mode=BrokerVerificationMode.DOCUMENTATION)
    assert core.discovery_receipt_id == "DISC-1"
    assert core.discovery_receipt_fingerprint == discovery.full_receipt_fingerprint
    assert core.reconstruction_receipt_ids == ("RECON-1",)
    assert core.reconstruction_receipt_fingerprints == (reconstruction.full_receipt_fingerprint,)
    assert core.capability_source_ids == ("SRC-SINOPAC-LOGIN-001",)
    assert not hasattr(core,"ready") and not hasattr(core,"finalize")


def test_rf01_full_receipt_fingerprints_bind_all_provenance_and_round_trip() -> None:
    _,discovery,reconstruction=_trusted_resolver_fixture()
    assert BrokerDiscoveryReceipt.model_validate(discovery.model_dump(mode="json")).full_receipt_fingerprint == discovery.full_receipt_fingerprint
    assert BrokerReconstructionReceipt.model_validate(reconstruction.model_dump(mode="json")).full_receipt_fingerprint == reconstruction.full_receipt_fingerprint

    changed_discovery=BrokerDiscoveryReceipt(**{**discovery.model_dump(exclude={"full_receipt_fingerprint"}),"producer_id":"OTHER"})
    changed_discovery_contract=BrokerDiscoveryReceipt(**{**discovery.model_dump(exclude={"full_receipt_fingerprint"}),"contract_version":"V2"})
    assert changed_discovery.full_receipt_fingerprint != discovery.full_receipt_fingerprint
    assert changed_discovery_contract.full_receipt_fingerprint != discovery.full_receipt_fingerprint

    changed_input=BrokerReconstructionReceipt(**{**reconstruction.model_dump(exclude={"full_receipt_fingerprint","input_coverage_fingerprint","accepted_fill_ids","output_fingerprint"}),"local_fill_ids":("OTHER-FILL",)})
    changed_producer=BrokerReconstructionReceipt(**{**reconstruction.model_dump(exclude={"full_receipt_fingerprint"}),"producer_id":"OTHER"})
    changed_contract=BrokerReconstructionReceipt(**{**reconstruction.model_dump(exclude={"full_receipt_fingerprint"}),"contract_version":"V2"})
    assert changed_input.output_fingerprint == reconstruction.output_fingerprint
    assert changed_input.full_receipt_fingerprint != reconstruction.full_receipt_fingerprint
    assert changed_producer.full_receipt_fingerprint != reconstruction.full_receipt_fingerprint
    assert changed_contract.full_receipt_fingerprint != reconstruction.full_receipt_fingerprint
    supplied=BrokerReconstructionReceipt(**{**reconstruction.model_dump(),"full_receipt_fingerprint":"CALLER-VALUE"})
    assert supplied.full_receipt_fingerprint == reconstruction.full_receipt_fingerprint


def test_rf01_reconstruction_full_fingerprint_binds_accepted_fill_set() -> None:
    _,_,reconstruction=_trusted_resolver_fixture()
    fill=Fill(fill_id="FILL-1",order_id="ORDER-1",event_id="EVENT-1",broker_trade_id="TRADE-1",broker_deal_id="DEAL-1",quantity=1,price=Decimal("100"),occurred_at=NOW,correlation_id="CORR-1",causation_id="EVENT-1")
    changed_plan=BrokerReconstructionPlan(status=OrderStatus.PARTIALLY_FILLED,accepted_fills=(fill,),filled_quantity=1,average_fill_price=Decimal("100"),material_change=True)
    changed=BrokerReconstructionReceipt(**{**reconstruction.model_dump(exclude={"full_receipt_fingerprint","input_coverage_fingerprint","accepted_fill_ids","output_fingerprint"}),"plan":changed_plan})
    assert changed.full_receipt_fingerprint != reconstruction.full_receipt_fingerprint


def test_rf01_resolver_sorts_receipt_ids_and_rejects_duplicates() -> None:
    resolver,_,reconstruction=_trusted_resolver_fixture()
    second=BrokerReconstructionReceipt(**{**reconstruction.model_dump(exclude={"full_receipt_fingerprint"}),"reconstruction_receipt_id":"RECON-2","recorded_at":NOW+timedelta(seconds=1)})
    original_get=resolver._recovery.get_reconstruction_receipt
    resolver._recovery.get_reconstruction_receipt=lambda *,reconstruction_receipt_id,account: second if reconstruction_receipt_id=="RECON-2" else original_get(reconstruction_receipt_id=reconstruction_receipt_id,account=account)
    values=dict(account=ACCOUNT,recovery_generation=4,recovery_cut_fingerprint="CUT",discovery_run_id="DISC-1",expected_snapshot_id="SNAP-1",broker_observation_id="OBS-1",required_capabilities=(BrokerCapability.ACCOUNT_QUERY,),required_verification_mode=BrokerVerificationMode.DOCUMENTATION)
    core=resolver.resolve(reconstruction_receipt_ids=("RECON-2","RECON-1"),**values)
    assert core.reconstruction_receipt_ids == ("RECON-1","RECON-2")
    assert core.reconstruction_receipt_fingerprints == (reconstruction.full_receipt_fingerprint,second.full_receipt_fingerprint)
    with pytest.raises(TrustedRecoveryEvidenceError,match="duplicate"):
        resolver.resolve(reconstruction_receipt_ids=("RECON-1","RECON-1"),**values)


@pytest.mark.parametrize("updates",[
    {"recovery_generation":5},
    {"recovery_cut_fingerprint":"OTHER"},
    {"discovery_run_id":"MISSING"},
    {"reconstruction_receipt_ids":("MISSING",)},
    {"expected_snapshot_id":"MISSING"},
    {"broker_observation_id":"MISSING"},
    {"required_verification_mode":BrokerVerificationMode.PRODUCTION},
])
def test_trusted_resolver_fails_closed_on_missing_stale_or_unverified_material(updates) -> None:
    resolver,_,_= _trusted_resolver_fixture()
    values=dict(account=ACCOUNT,recovery_generation=4,recovery_cut_fingerprint="CUT",discovery_run_id="DISC-1",reconstruction_receipt_ids=("RECON-1",),expected_snapshot_id="SNAP-1",broker_observation_id="OBS-1",required_capabilities=(BrokerCapability.ACCOUNT_QUERY,),required_verification_mode=BrokerVerificationMode.DOCUMENTATION)
    values.update(updates)
    with pytest.raises(TrustedRecoveryEvidenceError): resolver.resolve(**values)
