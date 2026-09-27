from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from persistence.account_authority import AccountAuthorityCommitReceipt, AccountRecoveryCheckpoint, AccountStateHead
from persistence.recovery import AccountReadinessEvaluation, ExecutionRestoreResult, ExecutionRestoreStatus, RecoveryCut
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
        with self._connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
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


__all__=["PostgresAccountReadinessGate","PostgresExecutionStateLoader","StaleAccountReadinessError"]
