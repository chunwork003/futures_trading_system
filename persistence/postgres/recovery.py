from __future__ import annotations

from typing import Any

from persistence.account_authority import (
    AccountAuthorityCommitReceipt,
    AccountRecoveryCheckpoint,
    AccountStateHead,
)
from persistence.recovery import (
    AccountReadinessEvaluation,
    ExecutionRestoreResult,
    ExecutionRestoreStatus,
    RecoveryCut,
)
from trading.account import BrokerAccount


class PostgresExecutionStateLoader:
    """以 caller-owned PostgreSQL repeatable snapshot 讀取 coherent local cut；不 repair、commit 或呼叫 broker。"""

    def __init__(self, connection: Any) -> None:
        self._connection=connection

    def load(self, account: BrokerAccount) -> ExecutionRestoreResult:
        with self._connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            cursor.execute(
                "SELECT h.broker,h.account_ref,h.current_revision,h.initialized,"
                "c.checkpoint_json,r.receipt_json,"
                "EXISTS (SELECT 1 FROM trading.expected_position_snapshots s WHERE s.snapshot_id=c.expected_snapshot_id) "
                "FROM trading.account_state_heads h "
                "LEFT JOIN trading.account_recovery_checkpoints c ON c.broker=h.broker AND c.account_ref=h.account_ref AND c.account_revision=h.current_revision "
                "LEFT JOIN trading.account_authority_commit_receipts r ON r.authority_commit_id=c.authority_commit_id "
                "WHERE h.broker=%s AND h.account_ref=%s",
                (account.broker,account.account_ref),
            )
            row=cursor.fetchone()
            if row is None:
                return ExecutionRestoreResult(
                    status=ExecutionRestoreStatus.RESTORE_FAILURE,
                    evidence=("account lifecycle authority head is missing",),
                )
            head=AccountStateHead(broker=row[0],account_ref=row[1],current_revision=row[2],initialized=row[3])
            if not head.initialized:
                return ExecutionRestoreResult(
                    status=ExecutionRestoreStatus.BASELINE_NOT_ESTABLISHED,
                    evidence=("reserved account authority revision zero proves baseline not established",),
                )
            if row[4] is None or row[5] is None or not row[6]:
                return ExecutionRestoreResult(
                    status=ExecutionRestoreStatus.RESTORE_FAILURE,
                    evidence=("account authority checkpoint closure is incomplete",),
                )
            checkpoint=AccountRecoveryCheckpoint.model_validate(row[4])
            receipt=AccountAuthorityCommitReceipt.model_validate(row[5])
            cursor.execute(
                "SELECT generation,ingress_version FROM trading.account_recovery_controls WHERE broker=%s AND account_ref=%s",
                (account.broker,account.account_ref),
            )
            control=cursor.fetchone()
            cursor.execute(
                "SELECT COUNT(*),(SELECT COUNT(*) FROM trading.broker_report_applications a JOIN trading.broker_report_inbox i ON i.ingress_id=a.ingress_id WHERE i.broker=%s AND i.account_ref=%s) FROM trading.broker_report_inbox i WHERE i.broker=%s AND i.account_ref=%s",
                (account.broker,account.account_ref,account.broker,account.account_ref),
            )
            evidence_counts=cursor.fetchone()
            cursor.execute(
                "SELECT unresolved_attempt_id FROM trading.broker_action_heads WHERE broker=%s AND account_ref=%s AND unresolved_attempt_id IS NOT NULL ORDER BY unresolved_attempt_id",
                (account.broker,account.account_ref),
            )
            unresolved=tuple(row[0] for row in cursor.fetchall())
        try:
            cut=RecoveryCut(
                account=account,
                head=head,
                checkpoint=checkpoint,
                receipt=receipt,
                recovery_generation=None if control is None else control[0],
                recovery_ingress_version=None if control is None else control[1],
                inbox_count=evidence_counts[0],
                application_count=evidence_counts[1],
                unresolved_broker_action_ids=unresolved,
            )
        except (TypeError,ValueError) as exc:
            return ExecutionRestoreResult(
                status=ExecutionRestoreStatus.RESTORE_FAILURE,
                evidence=(f"recovery cut validation failed: {exc}",),
            )
        return ExecutionRestoreResult(
            status=ExecutionRestoreStatus.VALID,
            cut=cut,
            evidence=("coherent repeatable-read local recovery cut validated",),
        )


class StaleAccountReadinessError(RuntimeError):
    """Evaluation cut 與 final local currentness 不同；caller 必須重新評估，不得 silent activate。"""


class PostgresAccountReadinessGate:
    """在 caller-owned local transaction 重驗 exact revision/frontier；不執行 broker I/O 或 economic mutation。"""

    def __init__(self,connection: Any) -> None: self._connection=connection

    def revalidate(self,evaluation: AccountReadinessEvaluation) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                "SELECT current_revision FROM trading.account_state_heads WHERE broker=%s AND account_ref=%s FOR SHARE",
                (evaluation.account.broker,evaluation.account.account_ref),
            )
            head=cursor.fetchone()
            cursor.execute(
                "SELECT generation,ingress_version FROM trading.account_recovery_controls WHERE broker=%s AND account_ref=%s FOR SHARE",
                (evaluation.account.broker,evaluation.account.account_ref),
            )
            control=cursor.fetchone()
            cursor.execute(
                "SELECT COUNT(*),(SELECT COUNT(*) FROM trading.broker_report_applications a JOIN trading.broker_report_inbox i ON i.ingress_id=a.ingress_id WHERE i.broker=%s AND i.account_ref=%s) FROM trading.broker_report_inbox i WHERE i.broker=%s AND i.account_ref=%s",
                (evaluation.account.broker,evaluation.account.account_ref,evaluation.account.broker,evaluation.account.account_ref),
            )
            counts=cursor.fetchone()
            cursor.execute(
                "SELECT unresolved_attempt_id FROM trading.broker_action_heads WHERE broker=%s AND account_ref=%s AND unresolved_attempt_id IS NOT NULL ORDER BY unresolved_attempt_id",
                (evaluation.account.broker,evaluation.account.account_ref),
            )
            unresolved=tuple(row[0] for row in cursor.fetchall())
        actual_control=(None,None) if control is None else tuple(control)
        expected_control=(evaluation.recovery_generation,evaluation.recovery_ingress_version)
        if head is None or head[0] != evaluation.account_revision or actual_control != expected_control or tuple(counts) != (evaluation.inbox_count,evaluation.application_count) or unresolved != evaluation.unresolved_broker_action_ids:
            raise StaleAccountReadinessError("account recovery cut/currentness changed; reevaluation required")


__all__=["PostgresAccountReadinessGate","PostgresExecutionStateLoader","StaleAccountReadinessError"]
