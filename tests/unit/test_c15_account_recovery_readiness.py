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
    TrustedReconciliationBlockerResolver,
    RecoveryRootIntegrityError,
    RecoveryOrderRoot,
    RecoveryRootResolver,
    RecoveryRootSetEvidence,
    RecoveryRootSource,
    RecoveryClosureEvidence,
    RecoveryClosureIntegrityError,
    RecoveryClosureResolver,
    evaluate_account_readiness,
)
from persistence.broker_recovery import ExecutionContinuityEpoch
from persistence.reconciliation import ReconciliationCaseVersion
from persistence.broker_recovery import BrokerDiscoveryReceipt, BrokerReconstructionReceipt, BrokerReportInboxEntry
from persistence.broker_action import BrokerActionHead, BrokerActionKind
from persistence.events import TradingEvent
from persistence.execution import order_event_as_trading_event
from persistence.account import AccountPositionSnapshot, BrokerPositionObservation
from adapters.capabilities import BrokerCapability, BrokerVerificationMode, StaticBrokerCapabilityProvider
from adapters.sinopac.capabilities import SINOPAC_CAPABILITY_REGISTRY_SNAPSHOT
from trading.broker_recovery import BrokerDealSetCompleteness, BrokerReconstructionPlan
from trading.execution import Fill, Order, OrderEvent, OrderStatus, OrderType, PositionEffect
from trading.account import PositionDirection
from trading.broker_recovery import BrokerDiscoveryIntegrity, BrokerDiscoveryResult, DiscoveryCompleteness, ExactMatchCardinality
from trading.account import BrokerAccount
from trading.reconciliation import ReconciliationPolicy, ReconciliationResult, ReconciliationStatus
from trading.reconciliation import create_reconciliation_case, resolve_reconciliation_case, ReconciliationCaseState, ReconciliationCaseError

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


def _case_version(case_id: str, policy: ReconciliationPolicy, *, account=ACCOUNT, version=1):
    result=ReconciliationResult(status=ReconciliationStatus.INTERNAL_ONLY,expected=None,actual=None)
    case=create_reconciliation_case(case_id=case_id,account=account,result=result,policy=policy)
    return ReconciliationCaseVersion(case_id=case_id,version=version,recorded_at=NOW,reconciliation_case=case)


class _CaseRepo:
    def __init__(self, versions=(), error=None): self.versions,self.error,self.accounts=versions,error,[]
    def unresolved(self, account):
        self.accounts.append(account)
        if self.error is not None: raise self.error
        return tuple(item for item in self.versions if item.reconciliation_case.account == account and item.reconciliation_case.state is not ReconciliationCaseState.RESOLVED)


@pytest.mark.parametrize(("versions","state"),[
    ((_case_version("HALT",ReconciliationPolicy.STRICT_HALT),),ReconciliationCaseState.HALT),
    ((_case_version("REVIEW",ReconciliationPolicy.MANUAL_REVIEW),),ReconciliationCaseState.REVIEW_REQUIRED),
    ((_case_version("REVIEW",ReconciliationPolicy.MANUAL_REVIEW),_case_version("HALT",ReconciliationPolicy.STRICT_HALT)),ReconciliationCaseState.HALT),
    ((),None),
])
def test_c1_resolver_reuses_c13_blocking_precedence(versions,state) -> None:
    repo=_CaseRepo(versions)
    result=TrustedReconciliationBlockerResolver(repo).resolve(account=ACCOUNT)
    assert result.blocking_state is state
    assert result.unresolved_case_ids == tuple(sorted(item.case_id for item in versions))
    assert repo.accounts == [ACCOUNT]
    assert not hasattr(result,"ready") and not hasattr(result,"finalize")


def test_c1_resolver_is_account_scoped_and_propagates_legacy_failure() -> None:
    other=BrokerAccount(broker="SINOPAC",account_ref="B")
    repo=_CaseRepo((_case_version("OTHER",ReconciliationPolicy.STRICT_HALT,account=other),))
    result=TrustedReconciliationBlockerResolver(repo).resolve(account=ACCOUNT)
    assert result.blocking_state is None and result.unresolved_case_ids == ()
    error=ReconciliationCaseError("legacy NULL scope")
    with pytest.raises(ReconciliationCaseError,match="legacy"):
        TrustedReconciliationBlockerResolver(_CaseRepo(error=error)).resolve(account=ACCOUNT)


def test_c1_resolver_output_is_deterministic_and_caller_cannot_bypass_resolution() -> None:
    first=_case_version("B",ReconciliationPolicy.MANUAL_REVIEW)
    second=_case_version("A",ReconciliationPolicy.STRICT_HALT)
    left=TrustedReconciliationBlockerResolver(_CaseRepo((first,second))).resolve(account=ACCOUNT)
    right=TrustedReconciliationBlockerResolver(_CaseRepo((second,first))).resolve(account=ACCOUNT)
    assert left == right
    assert left.unresolved_case_ids == ("A","B")
    with pytest.raises(TypeError):
        TrustedReconciliationBlockerResolver(_CaseRepo(())).resolve(account=ACCOUNT,blocking=True,semantic_fingerprint="FORGED")


def _order(order_id="ORDER-1",status=OrderStatus.PENDING):
    return Order(order_id=order_id,intent_id="INTENT",correlation_id="CORR",broker_client_order_ref="CLIENT",instrument_id=1,contract_id=2,direction=PositionDirection.LONG,position_effect=PositionEffect.OPEN,order_type=OrderType.MARKET,quantity=1,status=status,created_at=NOW,updated_at=NOW)


def _root_resolver(*,heads=(),orders=None,event=None,recovery=None,expected=None):
    trusted,_,_= _trusted_resolver_fixture()
    core=trusted.resolve(account=ACCOUNT,recovery_generation=4,recovery_cut_fingerprint="CUT",discovery_run_id="DISC-1",reconstruction_receipt_ids=("RECON-1",),expected_snapshot_id="SNAP-1",broker_observation_id="OBS-1",required_capabilities=(BrokerCapability.ACCOUNT_QUERY,),required_verification_mode=BrokerVerificationMode.DOCUMENTATION)
    event=event or TradingEvent(event_id="EVENT",event_type="ORDER",source="OMS",entity_type="ORDER",entity_id="ORDER-1",occurred_at=NOW,received_at=NOW,sequence=0,event_version=1,idempotency_scope="S",idempotency_key="K",payload_json={})
    class Actions:
        def list_heads(self,account): return tuple(heads)
    class Orders:
        def get(self,order_id): return (orders or {}).get(order_id)
    class Events:
        def get(self,event_id): return event if event_id=="EVENT" else None
    resolver=RecoveryRootResolver(broker_action_repository=Actions(),order_repository=Orders(),broker_recovery_repository=recovery or trusted._recovery,expected_snapshot_repository=expected or trusted._expected,event_ledger_repository=Events())
    return resolver,core


def _report(payload,*,account=ACCOUNT,generation=4,ingress_id="IN-1"):
    return BrokerReportInboxEntry(ingress_id=ingress_id,broker=account.broker,account_ref=account.account_ref,generation=generation,received_at=NOW,report_type="ORDER",payload_fingerprint="PF",payload_json=payload)


def test_c2a_root_sources_dedupe_and_preserve_all_categories() -> None:
    head=BrokerActionHead(broker="SINOPAC",account_ref="A",order_id="ORDER-1",action=BrokerActionKind.SUBMIT,version=1,unresolved_attempt_id="ATTEMPT")
    resolver,core=_root_resolver(heads=(head,),orders={"ORDER-1":_order()})
    result=resolver.resolve(trusted_core=core,material_report_entries=(_report({"order_id":"ORDER-1"}),_report({},ingress_id="AMBIG")))
    assert result.order_ids == ("ORDER-1",)
    assert set(result.roots[0].sources) == set(RecoveryRootSource)
    assert result.ambiguous_report_ingress_ids == ("AMBIG",)
    assert not hasattr(result,"ready") and not hasattr(result,"finalize")


def test_c2a_terminal_resolved_head_is_not_root_but_unresolved_is_root() -> None:
    resolved=BrokerActionHead(broker="SINOPAC",account_ref="A",order_id="TERMINAL",action=BrokerActionKind.SUBMIT,version=2)
    unresolved=resolved.model_copy(update={"order_id":"UNRESOLVED","unresolved_attempt_id":"ATTEMPT"})
    resolver,core=_root_resolver(heads=(resolved,unresolved),orders={"TERMINAL":_order("TERMINAL",OrderStatus.FILLED),"UNRESOLVED":_order("UNRESOLVED",OrderStatus.FILLED)})
    result=resolver.resolve(trusted_core=core,material_report_entries=())
    assert "TERMINAL" not in result.order_ids and "UNRESOLVED" in result.order_ids


def test_c2a_missing_head_order_and_reconstruction_binding_fail_closed() -> None:
    head=BrokerActionHead(broker="SINOPAC",account_ref="A",order_id="MISSING",action=BrokerActionKind.SUBMIT,version=1)
    resolver,core=_root_resolver(heads=(head,))
    with pytest.raises(RecoveryRootIntegrityError,match="missing Order"): resolver.resolve(trusted_core=core,material_report_entries=())
    resolver,core=_root_resolver()
    with pytest.raises(RecoveryRootIntegrityError,match="binding"): resolver.resolve(trusted_core=core.model_copy(update={"reconstruction_receipt_fingerprints":("BAD",)}),material_report_entries=())
    class MissingRecovery:
        def get_reconstruction_receipt(self,**kwargs): return None
    resolver,core=_root_resolver(recovery=MissingRecovery())
    with pytest.raises(RecoveryRootIntegrityError,match="missing"): resolver.resolve(trusted_core=core,material_report_entries=())


def test_c2a_snapshot_event_and_report_integrity_fail_closed() -> None:
    resolver,core=_root_resolver(event=TradingEvent(event_id="EVENT",event_type="X",source="OMS",entity_type="ACCOUNT",entity_id="ORDER-1",occurred_at=NOW,received_at=NOW,sequence=0,event_version=1,idempotency_scope="S",idempotency_key="K",payload_json={}))
    with pytest.raises(RecoveryRootIntegrityError,match="not ORDER"): resolver.resolve(trusted_core=core,material_report_entries=())
    class MissingExpected:
        def get_exact(self,**kwargs): return None
    resolver,core=_root_resolver(expected=MissingExpected())
    with pytest.raises(RecoveryRootIntegrityError,match="snapshot"): resolver.resolve(trusted_core=core,material_report_entries=())
    resolver,core=_root_resolver()
    for entry in (_report({"order_id":1}),_report({"order_id":"  "}),_report({"order_id":"ORDER"},generation=5)):
        with pytest.raises(RecoveryRootIntegrityError): resolver.resolve(trusted_core=core,material_report_entries=(entry,))


def test_c2a_root_set_is_deterministic_and_caller_cannot_inject_roots() -> None:
    resolver,core=_root_resolver()
    left=resolver.resolve(trusted_core=core,material_report_entries=(_report({"order_id":"Z"},ingress_id="Z"),_report({"order_id":"A"},ingress_id="A")))
    right=resolver.resolve(trusted_core=core,material_report_entries=(_report({"order_id":"A"},ingress_id="A"),_report({"order_id":"Z"},ingress_id="Z")))
    assert left == right
    with pytest.raises(TypeError): resolver.resolve(trusted_core=core,material_report_entries=(),order_ids=("FORGED",),root_set_fingerprint="FORGED")


def test_rf01_head_exact_read_rejects_mismatched_embedded_order_id() -> None:
    head=BrokerActionHead(broker="SINOPAC",account_ref="A",order_id="REQUESTED",action=BrokerActionKind.SUBMIT,version=1)
    resolver,core=_root_resolver(heads=(head,),orders={"REQUESTED":_order("OTHER")})
    with pytest.raises(RecoveryRootIntegrityError,match="identity"):
        resolver.resolve(trusted_core=core,material_report_entries=())


@pytest.mark.parametrize("snapshot",[
    AccountPositionSnapshot(snapshot_id="OTHER",broker="SINOPAC",account_ref="A",effective_at=NOW,recorded_at=NOW,source_event_id="EVENT",positions=()),
    AccountPositionSnapshot(snapshot_id="SNAP-1",broker="SINOPAC",account_ref="B",effective_at=NOW,recorded_at=NOW,source_event_id="EVENT",positions=()),
])
def test_rf01_expected_snapshot_exact_read_rejects_identity_or_account_mismatch(snapshot) -> None:
    class Expected:
        def get_exact(self,**kwargs): return snapshot
    resolver,core=_root_resolver(expected=Expected())
    with pytest.raises(RecoveryRootIntegrityError,match="snapshot identity"):
        resolver.resolve(trusted_core=core,material_report_entries=())


def test_rf01_source_event_exact_read_rejects_mismatched_embedded_event_id() -> None:
    event=TradingEvent(event_id="OTHER",event_type="ORDER",source="OMS",entity_type="ORDER",entity_id="ORDER-1",occurred_at=NOW,received_at=NOW,sequence=0,event_version=1,idempotency_scope="S",idempotency_key="K",payload_json={})
    resolver,core=_root_resolver(event=event)
    with pytest.raises(RecoveryRootIntegrityError,match="event identity"):
        resolver.resolve(trusted_core=core,material_report_entries=())


def test_rf01_matching_exact_reads_preserve_deterministic_output_and_no_authority_surface() -> None:
    resolver,core=_root_resolver()
    left=resolver.resolve(trusted_core=core,material_report_entries=())
    right=resolver.resolve(trusted_core=core,material_report_entries=())
    assert left == right
    assert not hasattr(left,"ready") and not hasattr(left,"finalize") and not hasattr(left,"handoff")


def _closure_event(sequence=0, previous=None, status=OrderStatus.PENDING, **updates):
    values=dict(event_id=f"EV-{sequence}",order_id="ORDER-1",correlation_id="CORR",causation_id="INTENT" if sequence==0 else f"EV-{sequence-1}",idempotency_key=f"KEY-{sequence}",sequence=sequence,previous_status=previous,status=status,occurred_at=NOW,received_at=NOW)
    values.update(updates)
    return order_event_as_trading_event(OrderEvent(**values))


def _closure_root_set(*, ambiguous=("AMBIG-1",)):
    return RecoveryRootSetEvidence(account=ACCOUNT,recovery_generation=4,roots=(RecoveryOrderRoot(order_id="ORDER-1",sources=(RecoveryRootSource.RECONSTRUCTION_RECEIPT,)),),order_ids=(),ambiguous_report_ingress_ids=ambiguous)


class _ClosureOrders:
    def __init__(self,item): self.item=item; self.calls=[]
    def get(self,order_id): self.calls.append(order_id); return self.item


class _ClosureFills:
    def __init__(self,items=()): self.items=tuple(items); self.calls=[]
    def list_by_order(self,order_id): self.calls.append(order_id); return self.items


class _ClosureEvents:
    def __init__(self,items): self.items=tuple(items); self.calls=[]
    def list_after(self,*args): self.calls.append(args); return self.items


def _closure_resolver(*,order=None,fills=(),events=None):
    order=order or _order()
    events=events if events is not None else (_closure_event(),)
    repositories=(_ClosureOrders(order),_ClosureFills(fills),_ClosureEvents(events))
    return RecoveryClosureResolver(order_repository=repositories[0],fill_repository=repositories[1],event_ledger_repository=repositories[2]),repositories


def test_c2b_exact_zero_fill_closure_is_deterministic_and_bounded() -> None:
    resolver,repositories=_closure_resolver()
    left=resolver.resolve(root_set=_closure_root_set())
    right=resolver.resolve(root_set=_closure_root_set())
    assert isinstance(left,RecoveryClosureEvidence) and left == right
    assert left.order_ids == ("ORDER-1",)
    assert left.ambiguous_report_ingress_ids == ("AMBIG-1",)
    assert repositories[0].calls == ["ORDER-1","ORDER-1"]
    assert repositories[1].calls == ["ORDER-1","ORDER-1"]
    assert repositories[2].calls == [("OMS","ORDER","ORDER-1",-1,2)]*2
    assert not hasattr(left,"ready") and not hasattr(left,"finalize") and not hasattr(left,"handoff")


@pytest.mark.parametrize("events,match",[
    ((),"sequence"),
    ((_closure_event(1,OrderStatus.PENDING,OrderStatus.SUBMITTED),),"sequence"),
    ((_closure_event(),_closure_event()),"duplicate"),
    ((_closure_event(),_closure_event(2,OrderStatus.PENDING,OrderStatus.SUBMITTED)),"sequence"),
    ((TradingEvent(**{**_closure_event().model_dump(),"source":"OTHER"}),),"envelope"),
    ((TradingEvent(**{**_closure_event().model_dump(),"idempotency_scope":"OTHER"}),),"scope"),
    ((TradingEvent(**{**_closure_event().model_dump(),"payload_json":{"status":"PENDING"}}),),"payload"),
])
def test_c2b_invalid_event_closure_fails_closed(events,match) -> None:
    resolver,_=_closure_resolver(events=events)
    with pytest.raises(RecoveryClosureIntegrityError,match=match): resolver.resolve(root_set=_closure_root_set())


def test_c2b_full_fill_closure_validates_economics_and_material_fingerprint() -> None:
    events=(_closure_event(),_closure_event(1,OrderStatus.PENDING,OrderStatus.FILLED))
    first=Fill(fill_id="F1",order_id="ORDER-1",event_id="EV-1",correlation_id="CORR",causation_id="EV-1",quantity=1,price=Decimal("100"),occurred_at=NOW)
    second=Fill(fill_id="F2",order_id="ORDER-1",event_id="EV-1",correlation_id="CORR",causation_id="EV-1",quantity=1,price=Decimal("102"),occurred_at=NOW)
    order=_order(status=OrderStatus.FILLED).model_copy(update={"quantity":2,"filled_quantity":2,"average_fill_price":Decimal("101"),"version":1})
    left,_=_closure_resolver(order=order,fills=(second,first),events=events)
    right,_=_closure_resolver(order=order,fills=(first,second),events=events)
    assert left.resolve(root_set=_closure_root_set()) == right.resolve(root_set=_closure_root_set())
    changed=second.model_copy(update={"price":Decimal("104")})
    invalid,_=_closure_resolver(order=order,fills=(first,changed),events=events)
    with pytest.raises(RecoveryClosureIntegrityError,match="average"): invalid.resolve(root_set=_closure_root_set())


@pytest.mark.parametrize("fills,order_update,match",[
    ((Fill(fill_id="F1",order_id="OTHER",event_id="EV-1",correlation_id="CORR",causation_id="EV-1",quantity=1,price=Decimal("100"),occurred_at=NOW),),{},"order"),
    ((Fill(fill_id="F1",order_id="ORDER-1",event_id="OTHER",correlation_id="CORR",causation_id="OTHER",quantity=1,price=Decimal("100"),occurred_at=NOW),),{},"event"),
    ((Fill(fill_id="F1",order_id="ORDER-1",event_id="EV-0",correlation_id="OTHER",causation_id="EV-0",quantity=1,price=Decimal("100"),occurred_at=NOW),),{},"correlation"),
    ((),{"filled_quantity":1,"average_fill_price":Decimal("100")},"economic"),
])
def test_c2b_fill_and_projection_integrity_fail_closed(fills,order_update,match) -> None:
    order=_order().model_copy(update=order_update)
    resolver,_=_closure_resolver(order=order,fills=fills)
    with pytest.raises(RecoveryClosureIntegrityError,match=match): resolver.resolve(root_set=_closure_root_set())


def test_c2b_missing_or_mismatched_exact_order_and_caller_injection_fail() -> None:
    resolver,_=_closure_resolver(order=None)
    resolver._orders.item=None
    with pytest.raises(RecoveryClosureIntegrityError,match="missing"): resolver.resolve(root_set=_closure_root_set())
    resolver,_=_closure_resolver(order=_order("OTHER"))
    with pytest.raises(RecoveryClosureIntegrityError,match="identity"): resolver.resolve(root_set=_closure_root_set())
    resolver,_=_closure_resolver()
    with pytest.raises(TypeError): resolver.resolve(root_set=_closure_root_set(),order_ids=("OTHER",),closure_fingerprint="FORGED")
