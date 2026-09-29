from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from persistence.account_authority import AccountAuthorityCommitReceipt, AccountRecoveryCheckpoint, AccountStateHead
from persistence.broker_action import BrokerActionHead
from persistence.broker_recovery import BrokerReportInboxEntry, ContinuityTransitionReceipt, ExecutionContinuityEpoch, ExecutionContinuityHead, SequenceGap
from persistence.postgres.broker_action import PostgresBrokerActionRepository
from persistence.postgres.reconciliation import PostgresReconciliationCaseRepository, PostgresReconciliationRunRepository
from persistence.recovery import (
    AccountReadinessEvaluation, ExecutionRestoreResult, ExecutionRestoreStatus,
    RecoveryClosureResolver, RecoveryCut, RecoveryRootResolver,
    TrustedReadinessEvidenceBundle, TrustedReconciliationBlockerResolver,
    TrustedRecoveryEvidenceError, TrustedRecoveryEvidenceResolver,
)
from adapters.capabilities import BrokerCapability, BrokerVerificationMode
from trading.account import BrokerAccount


def _canonical_anchor(row: Any) -> str:
    """把 DB exact row 固定為可比較 witness；不得以 count 或 wall-clock 猜 currentness。"""
    return json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str)


def _read_report_witness(cursor: Any,account: BrokerAccount) -> tuple[tuple[str,...],int,int]:
    cursor.execute(
        "WITH latest AS (SELECT DISTINCT ON (ingress_id,generation) ingress_id,generation,application_sequence,status FROM trading.broker_report_applications ORDER BY ingress_id,generation,application_sequence DESC), "
        "totals AS (SELECT ingress_id,generation,COUNT(*) AS application_count FROM trading.broker_report_applications GROUP BY ingress_id,generation) "
        "SELECT i.ingress_id,i.generation,i.payload_fingerprint,i.recovery_active_at_capture,l.application_sequence,l.status,COALESCE(t.application_count,0) "
        "FROM trading.broker_report_inbox i LEFT JOIN latest l ON l.ingress_id=i.ingress_id AND l.generation=i.generation "
        "LEFT JOIN totals t ON t.ingress_id=i.ingress_id AND t.generation=i.generation "
        "WHERE i.broker=%s AND i.account_ref=%s ORDER BY i.ingress_id,i.generation",
        (account.broker,account.account_ref),
    )
    rows=tuple(cursor.fetchall())
    return tuple(_canonical_anchor(tuple(row)) for row in rows),len(rows),sum(int(row[6]) for row in rows)


def _read_order_witness(cursor: Any,account: BrokerAccount) -> tuple[tuple[str,...],tuple[str,...]]:
    # BrokerActionHead 是既有的 durable BrokerAccount→Order scope authority；禁止信任 projection JSON 或 global scan。
    cursor.execute(
        "SELECT DISTINCT o.order_id,o.version,o.status,o.projection_json "
        "FROM trading.broker_action_heads h JOIN trading.orders o ON o.order_id=h.order_id "
        "WHERE h.broker=%s AND h.account_ref=%s "
        "AND o.status NOT IN ('FILLED','CANCELLED','REJECTED') ORDER BY o.order_id",
        (account.broker,account.account_ref),
    )
    order_rows=tuple(cursor.fetchall())
    order_ids=tuple(row[0] for row in order_rows)
    cursor.execute(
        "SELECT f.fill_id,f.order_id,f.event_id,f.quantity,f.price,f.occurred_at,f.broker_deal_id,f.fill_json "
        "FROM trading.fills f JOIN trading.broker_action_heads h ON h.order_id=f.order_id "
        "WHERE h.broker=%s AND h.account_ref=%s ORDER BY f.order_id,f.fill_id",
        (account.broker,account.account_ref),
    )
    fill_rows=tuple(cursor.fetchall())
    cursor.execute(
        "SELECT e.event_id,e.event_type,e.source,e.entity_id,e.occurred_at,e.received_at,e.sequence,e.event_version,"
        "e.idempotency_scope,e.idempotency_key,e.correlation_id,e.causation_id,e.payload_json "
        "FROM trading.event_ledger e JOIN trading.broker_action_heads h ON h.order_id=e.entity_id "
        "WHERE h.broker=%s AND h.account_ref=%s AND e.entity_type='ORDER' ORDER BY e.entity_id,e.sequence,e.event_id",
        (account.broker,account.account_ref),
    )
    event_rows=tuple(cursor.fetchall())
    anchors=[f"FILL:{_canonical_anchor(tuple(row))}" for row in fill_rows]
    anchors.extend(f"EVENT:{_canonical_anchor(tuple(row))}" for row in event_rows)
    return tuple(_canonical_anchor(tuple(row)) for row in order_rows),tuple(sorted(anchors))


def _read_currentness_witness(cursor: Any,account: BrokerAccount) -> tuple[tuple[str,...],tuple[str,...],tuple[str,...]]:
    """讀取 account-scoped continuity/gap/reconciliation exact rows；count 不能取代 current world。"""
    cursor.execute(
        "SELECT epoch_id,broker,account_ref,generation,trusted_current,historical_degradation,anchored_at,evidence_json "
        "FROM trading.execution_continuity_epochs WHERE broker=%s AND account_ref=%s ORDER BY epoch_id",
        (account.broker,account.account_ref),
    )
    continuity=tuple(_canonical_anchor(tuple(row)) for row in cursor.fetchall())
    cursor.execute(
        "SELECT gap_id,broker,account_ref,detected_at,evidence FROM trading.broker_sequence_gaps "
        "WHERE broker=%s AND account_ref=%s ORDER BY gap_id",
        (account.broker,account.account_ref),
    )
    gaps=tuple(_canonical_anchor(tuple(row)) for row in cursor.fetchall())
    cursor.execute(
        "SELECT DISTINCT ON (case_id) case_id,version,state,evidence,case_json FROM trading.reconciliation_case_history "
        "WHERE broker=%s AND account_ref=%s ORDER BY case_id,version DESC",
        (account.broker,account.account_ref),
    )
    reconciliation=tuple(_canonical_anchor(tuple(row)) for row in cursor.fetchall())
    return continuity,gaps,reconciliation


def _read_formal_run_witness(cursor: Any,account: BrokerAccount,run_id: str | None) -> tuple[str,...]:
    if run_id is None:
        return ()
    cursor.execute(
        "SELECT r.boundary_json,o.outcome_json FROM trading.reconciliation_runs r "
        "LEFT JOIN trading.reconciliation_run_outcomes o ON o.run_id=r.run_id "
        "WHERE r.run_id=%s AND r.broker=%s AND r.account_ref=%s",
        (run_id,account.broker,account.account_ref),
    )
    row=cursor.fetchone()
    return () if row is None else tuple(_canonical_anchor(item) for item in row if item is not None)


def _read_unresolved_actions(cursor: Any,account: BrokerAccount) -> tuple[str,...]:
    cursor.execute(
        "SELECT unresolved_attempt_id FROM trading.broker_action_heads WHERE broker=%s AND account_ref=%s AND unresolved_attempt_id IS NOT NULL ORDER BY unresolved_attempt_id",
        (account.broker,account.account_ref),
    )
    return tuple(row[0] for row in cursor.fetchall())


class PostgresExecutionStateLoader:
    """以 caller-owned repeatable snapshot 讀 exact recovery witness；不 repair、commit 或呼叫 broker。"""
    def __init__(self,connection: Any) -> None: self._connection=connection

    def load(self,account: BrokerAccount) -> ExecutionRestoreResult:
        """為獨立 restore 建立 read-only repeatable snapshot，再委派既有交易內讀取。"""
        with self._connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        return self._load_current_transaction(account)

    def _load_current_transaction(self,account: BrokerAccount) -> ExecutionRestoreResult:
        """使用 caller 目前交易讀取 coherent cut；不改交易模式、不鎖定或 finalize。"""
        with self._connection.cursor() as cursor:
            cursor.execute(
                "SELECT h.broker,h.account_ref,h.current_revision,h.initialized,c.checkpoint_json,r.receipt_json,"
                    "EXISTS (SELECT 1 FROM trading.expected_position_snapshots s WHERE s.snapshot_id=c.expected_snapshot_id) "
                    "FROM trading.account_state_heads h LEFT JOIN trading.account_recovery_checkpoints c ON c.broker=h.broker AND c.account_ref=h.account_ref AND c.account_revision=h.current_revision "
                    "LEFT JOIN trading.account_authority_commit_receipts r ON r.authority_commit_id=c.authority_commit_id WHERE h.broker=%s AND h.account_ref=%s",
                (account.broker,account.account_ref),
            )
            row=cursor.fetchone()
            if row is None:
                return ExecutionRestoreResult(status=ExecutionRestoreStatus.RESTORE_FAILURE,evidence=("account lifecycle authority head is missing",))
            try:
                head=AccountStateHead(broker=row[0],account_ref=row[1],current_revision=row[2],initialized=row[3])
            except ValidationError as exc:
                return ExecutionRestoreResult(status=ExecutionRestoreStatus.RESTORE_FAILURE,evidence=(f"account authority head validation failed: {exc}",))
            if not head.initialized:
                return ExecutionRestoreResult(status=ExecutionRestoreStatus.BASELINE_NOT_ESTABLISHED,evidence=("reserved account authority revision zero proves baseline not established",))
            if row[4] is None or row[5] is None or not row[6]:
                return ExecutionRestoreResult(status=ExecutionRestoreStatus.RESTORE_FAILURE,evidence=("account authority checkpoint closure is incomplete",))
            try:
                checkpoint=AccountRecoveryCheckpoint.model_validate(row[4])
                receipt=AccountAuthorityCommitReceipt.model_validate(row[5])
            except ValidationError as exc:
                return ExecutionRestoreResult(status=ExecutionRestoreStatus.RESTORE_FAILURE,evidence=(f"authority closure evidence validation failed: {exc}",))
            cursor.execute("SELECT generation,ingress_version,active FROM trading.account_recovery_controls WHERE broker=%s AND account_ref=%s",(account.broker,account.account_ref))
            control=cursor.fetchone()
            if control is None or not control[2]:
                return ExecutionRestoreResult(status=ExecutionRestoreStatus.RESTORE_FAILURE,evidence=("active account recovery control is missing",))
            reports,inbox_count,application_count=_read_report_witness(cursor,account)
            orders,fill_events=_read_order_witness(cursor,account)
            continuity,gaps,reconciliation=_read_currentness_witness(cursor,account)
            unresolved=_read_unresolved_actions(cursor,account)
        try:
            cut=RecoveryCut(account=account,head=head,checkpoint=checkpoint,receipt=receipt,recovery_generation=control[0],recovery_ingress_version=control[1],inbox_count=inbox_count,application_count=application_count,broker_report_witness=reports,current_nonterminal_order_anchors=orders,fill_event_validation_anchors=fill_events,unresolved_broker_action_ids=unresolved)
            cut=cut.model_copy(update={"continuity_epoch_witness":continuity,"sequence_gap_witness":gaps,"reconciliation_currentness_witness":reconciliation})
            cut=RecoveryCut.model_validate(cut.model_dump())
        except ValidationError as exc:
            return ExecutionRestoreResult(status=ExecutionRestoreStatus.RESTORE_FAILURE,evidence=(f"recovery cut validation failed: {exc}",))
        return ExecutionRestoreResult(status=ExecutionRestoreStatus.VALID,cut=cut,evidence=("coherent repeatable-read exact recovery cut validated",))


class StaleAccountReadinessError(RuntimeError):
    """Evaluation cut 與 final local currentness 不同；caller 必須重新評估，不得 silent activate。"""


class PostgresAccountReadinessGate:
    """在 caller-owned transaction 重驗完整 exact witness；不執行 broker I/O 或 economic mutation。"""
    def __init__(self,connection: Any) -> None: self._connection=connection

    def revalidate(self,evaluation: AccountReadinessEvaluation) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute("SELECT current_revision FROM trading.account_state_heads WHERE broker=%s AND account_ref=%s FOR SHARE",(evaluation.account.broker,evaluation.account.account_ref))
            head=cursor.fetchone()
            cursor.execute("SELECT generation,ingress_version,active FROM trading.account_recovery_controls WHERE broker=%s AND account_ref=%s FOR SHARE",(evaluation.account.broker,evaluation.account.account_ref))
            control=cursor.fetchone()
            reports,inbox_count,application_count=_read_report_witness(cursor,evaluation.account)
            orders,fill_events=_read_order_witness(cursor,evaluation.account)
            continuity,gaps,reconciliation=_read_currentness_witness(cursor,evaluation.account)
            unresolved=_read_unresolved_actions(cursor,evaluation.account)
            formal_run=_read_formal_run_witness(cursor,evaluation.account,evaluation.formal_run_id)
        actual_control=(None,None) if control is None or not control[2] else (control[0],control[1])
        expected_control=(evaluation.recovery_generation,evaluation.recovery_ingress_version)
        if (head is None or head[0] != evaluation.account_revision or actual_control != expected_control or inbox_count != evaluation.inbox_count or application_count != evaluation.application_count or reports != evaluation.broker_report_witness or orders != evaluation.current_nonterminal_order_anchors or fill_events != evaluation.fill_event_validation_anchors or continuity != evaluation.continuity_epoch_witness or gaps != evaluation.sequence_gap_witness or reconciliation != evaluation.reconciliation_currentness_witness or formal_run != evaluation.formal_run_witness or unresolved != evaluation.unresolved_broker_action_ids):
            raise StaleAccountReadinessError("account recovery cut/currentness changed; reevaluation required")


class PostgresTrustedReadinessEvidenceResolver:
    """重讀 exact durable owners 並組成同一 recovery world；只讀、不 commit、不授予 READY。"""

    def __init__(self, connection: Any, *, trusted_core_resolver: TrustedRecoveryEvidenceResolver, root_resolver: RecoveryRootResolver, closure_resolver: RecoveryClosureResolver) -> None:
        self._connection=connection
        self._trusted=trusted_core_resolver
        self._roots=root_resolver
        self._closure=closure_resolver

    @staticmethod
    def _decode(model, row: Any, *, missing: str):
        if row is None: raise TrustedRecoveryEvidenceError(missing)
        try: return model.model_validate_json(row[0]) if isinstance(row[0],str) else model.model_validate(row[0])
        except Exception as exc: raise TrustedRecoveryEvidenceError(f"{missing}: canonical decode failed") from exc

    def resolve(self, *, account: BrokerAccount, discovery_run_id: str, reconstruction_receipt_ids: tuple[str,...], broker_observation_id: str, formal_run_id: str, required_capabilities: tuple[BrokerCapability,...], required_verification_mode: BrokerVerificationMode) -> TrustedReadinessEvidenceBundle:
        restore=PostgresExecutionStateLoader(self._connection)._load_current_transaction(account)
        if restore.status is not ExecutionRestoreStatus.VALID or restore.cut is None:
            raise TrustedRecoveryEvidenceError("coherent account recovery cut is missing")
        cut=restore.cut
        with self._connection.cursor() as cursor:
            cursor.execute("SELECT generation,recovery_cut_revision,ingress_version,readiness_revision,active FROM trading.account_recovery_controls WHERE broker=%s AND account_ref=%s",(account.broker,account.account_ref)); control=cursor.fetchone()
            if control is None or not control[4]: raise TrustedRecoveryEvidenceError("active recovery control is missing")
            generation,cut_revision,ingress_version,readiness_revision,_=control
            if (generation,cut_revision,ingress_version)!=(cut.recovery_generation,cut.head.current_revision,cut.recovery_ingress_version): raise TrustedRecoveryEvidenceError("active recovery control world mismatch")
            cursor.execute("SELECT jsonb_build_object('broker',broker,'account_ref',account_ref,'generation',generation,'current_epoch_id',current_epoch_id,'transition_receipt_id',transition_receipt_id,'head_revision',head_revision,'readiness_revision',readiness_revision,'recorded_at',recorded_at) FROM trading.execution_continuity_heads WHERE broker=%s AND account_ref=%s",(account.broker,account.account_ref)); continuity_head=self._decode(ExecutionContinuityHead,cursor.fetchone(),missing="current continuity head is missing")
            cursor.execute("SELECT jsonb_build_object('epoch_id',epoch_id,'broker',broker,'account_ref',account_ref,'generation',generation,'trusted_current',trusted_current,'historical_degradation',historical_degradation,'anchored_at',anchored_at,'evidence',evidence_json) FROM trading.execution_continuity_epochs WHERE epoch_id=%s",(continuity_head.current_epoch_id,)); epoch=self._decode(ExecutionContinuityEpoch,cursor.fetchone(),missing="head-selected continuity epoch is missing")
            cursor.execute("SELECT receipt_json FROM trading.continuity_transition_receipts WHERE transition_id=%s",(continuity_head.transition_receipt_id,)); transition=self._decode(ContinuityTransitionReceipt,cursor.fetchone(),missing="head-selected continuity transition is missing")
            cursor.execute("SELECT jsonb_build_object('gap_id',gap_id,'broker',broker,'account_ref',account_ref,'detected_at',detected_at,'evidence',evidence) FROM trading.broker_sequence_gaps WHERE broker=%s AND account_ref=%s ORDER BY gap_id",(account.broker,account.account_ref)); gaps=tuple(SequenceGap.model_validate(row[0]) for row in cursor.fetchall())
            cursor.execute("SELECT report_json FROM trading.broker_report_inbox WHERE broker=%s AND account_ref=%s AND generation=%s ORDER BY ingress_id",(account.broker,account.account_ref,generation)); reports=tuple(BrokerReportInboxEntry.model_validate(row[0]) for row in cursor.fetchall())
        with self._connection.cursor() as cursor:
            report_witness,_,_=_read_report_witness(cursor,account)
        core=self._trusted.resolve(account=account,recovery_generation=generation,recovery_cut_fingerprint=cut.witness_fingerprint,discovery_run_id=discovery_run_id,reconstruction_receipt_ids=reconstruction_receipt_ids,expected_snapshot_id=cut.checkpoint.expected_snapshot_id,broker_observation_id=broker_observation_id,required_capabilities=required_capabilities,required_verification_mode=required_verification_mode)
        blocker=TrustedReconciliationBlockerResolver(PostgresReconciliationCaseRepository(self._connection)).resolve(account=account)
        run_repository=PostgresReconciliationRunRepository(self._connection)
        boundary=run_repository.get_boundary(formal_run_id); outcome=run_repository.get_outcome(formal_run_id)
        if boundary is None or outcome is None: raise TrustedRecoveryEvidenceError("exact formal reconciliation run is incomplete")
        root_set=self._roots.resolve(trusted_core=core,material_report_entries=reports)
        closure=self._closure.resolve(root_set=root_set)
        actions=PostgresBrokerActionRepository(self._connection).list_heads(account)
        return TrustedReadinessEvidenceBundle(account=account,recovery_generation=generation,recovery_cut_revision=cut_revision,ingress_version=ingress_version,readiness_revision=readiness_revision,recovery_cut_fingerprint=cut.witness_fingerprint,head=cut.head,checkpoint=cut.checkpoint,receipt=cut.receipt,continuity_head=continuity_head,continuity_epoch=epoch,continuity_transition=transition,sequence_gaps=gaps,broker_report_witness=report_witness,broker_action_heads=actions,reconciliation_blocker=blocker,trusted_core=core,formal_run_boundary=boundary,formal_run_outcome=outcome,root_set=root_set,closure=closure)


__all__=["PostgresAccountReadinessGate","PostgresExecutionStateLoader","PostgresTrustedReadinessEvidenceResolver","StaleAccountReadinessError"]
