from __future__ import annotations

from typing import Any

from persistence.reconciliation import (
    ReconciliationCaseVersion,
    ReconciliationRunBoundary,
    ReconciliationRunOutcome,
    reconciliation_blocker_semantic_fingerprint,
)
from persistence.postgres.readiness_fence import PostgresRecoveryReadinessFenceRepository
from trading.account import BrokerAccount
from trading.reconciliation import ReconciliationCaseError, ReconciliationCaseState


def _case_readiness_contribution(
    version: ReconciliationCaseVersion | None,
) -> str | None:
    """只投影 C13 blocker material；audit wrapper 不得使 readiness 失效。"""

    if (
        version is None
        or version.reconciliation_case.state is ReconciliationCaseState.RESOLVED
    ):
        return None
    return reconciliation_blocker_semantic_fingerprint((version,))


def _boundary_from_row(row: Any) -> ReconciliationRunBoundary | None:
    if row is None:
        return None
    return (
        ReconciliationRunBoundary.model_validate_json(row[0])
        if isinstance(row[0], str)
        else ReconciliationRunBoundary.model_validate(row[0])
    )


class PostgresReconciliationCaseRepository:
    """Append-only account-scoped case history；scope drift 與 legacy ambiguity 一律 fail closed。"""
    def __init__(self, connection: Any) -> None: self._connection = connection
    def append(self, version: ReconciliationCaseVersion) -> None:
        account = version.reconciliation_case.account
        fence = PostgresRecoveryReadinessFenceRepository(self._connection)
        token = fence.lock_active(account)
        with self._connection.cursor() as c:
            c.execute("SELECT broker,account_ref,case_json FROM trading.reconciliation_case_history WHERE case_id=%s ORDER BY version DESC LIMIT 1 FOR UPDATE", (version.case_id,))
            prior=c.fetchone()
            scope=(account.broker,account.account_ref)
            if prior is not None and tuple(prior[:2]) != scope:
                raise ReconciliationCaseError("reconciliation case account scope cannot change")
            prior_version = None if prior is None else (
                ReconciliationCaseVersion.model_validate_json(prior[2])
                if isinstance(prior[2], str)
                else ReconciliationCaseVersion.model_validate(prior[2])
            )
            prior_contribution = _case_readiness_contribution(prior_version)
            c.execute("INSERT INTO trading.reconciliation_case_history (case_id, version, broker, account_ref, recorded_at, state, actor_ref, evidence, case_json) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", (version.case_id, version.version, *scope, version.recorded_at, version.reconciliation_case.state.value, version.actor_ref, list(version.evidence), version.model_dump_json()))
        if token is not None and prior_contribution != _case_readiness_contribution(version):
            fence.advance_locked(token)
    def latest(self, case_id: str):
        with self._connection.cursor() as c:
            c.execute("SELECT case_json FROM trading.reconciliation_case_history WHERE case_id=%s ORDER BY version DESC LIMIT 1", (case_id,)); row=c.fetchone()
        if row is None: return None
        return ReconciliationCaseVersion.model_validate_json(row[0]) if isinstance(row[0], str) else ReconciliationCaseVersion.model_validate(row[0])
    def unresolved(self, account: BrokerAccount):
        with self._connection.cursor() as c:
            c.execute("SELECT EXISTS (SELECT 1 FROM trading.reconciliation_case_history WHERE broker IS NULL OR account_ref IS NULL)")
            ambiguous=c.fetchone()
            if ambiguous is not None and ambiguous[0]:
                raise ReconciliationCaseError("legacy reconciliation case scope is ambiguous")
            c.execute("SELECT DISTINCT ON (case_id) case_json FROM trading.reconciliation_case_history WHERE broker=%s AND account_ref=%s ORDER BY case_id, version DESC", (account.broker,account.account_ref)); rows=c.fetchall()
        items = (
            ReconciliationCaseVersion.model_validate_json(row[0])
            if isinstance(row[0], str)
            else ReconciliationCaseVersion.model_validate(row[0])
            for row in rows
        )
        return tuple(item for item in items if item.reconciliation_case.state.value != "RESOLVED")


class PostgresReconciliationRunRepository:
    """PostgreSQL append-only formal run audit；boundary 與 terminal outcome 均由 caller transaction 控制。"""

    def __init__(self,connection: Any) -> None: self._connection=connection

    def establish(self,boundary: ReconciliationRunBoundary) -> None:
        fence = PostgresRecoveryReadinessFenceRepository(self._connection)
        token = fence.lock_active(boundary.account)
        with self._connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO trading.reconciliation_runs (run_id,broker,account_ref,established_at,boundary_json) VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING RETURNING run_id",
                (boundary.run_id,boundary.account.broker,boundary.account.account_ref,boundary.established_at,boundary.model_dump_json()),
            )
            if cursor.fetchone() is not None:
                if token is not None:
                    fence.advance_locked(token)
                return
            cursor.execute("SELECT boundary_json FROM trading.reconciliation_runs WHERE run_id=%s",(boundary.run_id,))
            row=cursor.fetchone()
            existing=None if row is None else ReconciliationRunBoundary.model_validate_json(row[0]) if isinstance(row[0],str) else ReconciliationRunBoundary.model_validate(row[0])
            if existing != boundary: raise ReconciliationCaseError("reconciliation run boundary identity conflict")

    def finalize(self,outcome: ReconciliationRunOutcome) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute("SELECT boundary_json FROM trading.reconciliation_runs WHERE run_id=%s",(outcome.run_id,))
            boundary = _boundary_from_row(cursor.fetchone())
        if boundary is None:
            raise ReconciliationCaseError("reconciliation run boundary is missing")
        fence = PostgresRecoveryReadinessFenceRepository(self._connection)
        token = fence.lock_active(boundary.account)
        with self._connection.cursor() as cursor:
            cursor.execute("SELECT boundary_json FROM trading.reconciliation_runs WHERE run_id=%s FOR UPDATE",(outcome.run_id,))
            locked_boundary = _boundary_from_row(cursor.fetchone())
            if locked_boundary is None:
                raise ReconciliationCaseError("reconciliation run boundary is missing")
            if locked_boundary != boundary:
                raise ReconciliationCaseError("reconciliation run boundary changed during finalize")
            cursor.execute(
                "INSERT INTO trading.reconciliation_run_outcomes (run_id,finalized_at,technical_outcome,input_qualification,outcome_json) VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING RETURNING run_id",
                (outcome.run_id,outcome.finalized_at,outcome.technical_outcome.value,outcome.input_qualification.value,outcome.model_dump_json()),
            )
            if cursor.fetchone() is not None:
                if token is not None:
                    fence.advance_locked(token)
                return
            cursor.execute("SELECT outcome_json FROM trading.reconciliation_run_outcomes WHERE run_id=%s",(outcome.run_id,))
            row=cursor.fetchone()
            existing=None if row is None else ReconciliationRunOutcome.model_validate_json(row[0]) if isinstance(row[0],str) else ReconciliationRunOutcome.model_validate(row[0])
            if existing != outcome: raise ReconciliationCaseError("reconciliation run terminal outcome conflict")

    def get_boundary(self,run_id: str):
        with self._connection.cursor() as cursor:
            cursor.execute("SELECT boundary_json FROM trading.reconciliation_runs WHERE run_id=%s",(run_id,)); row=cursor.fetchone()
        return None if row is None else ReconciliationRunBoundary.model_validate_json(row[0]) if isinstance(row[0],str) else ReconciliationRunBoundary.model_validate(row[0])

    def get_outcome(self,run_id: str):
        with self._connection.cursor() as cursor:
            cursor.execute("SELECT outcome_json FROM trading.reconciliation_run_outcomes WHERE run_id=%s",(run_id,)); row=cursor.fetchone()
        return None if row is None else ReconciliationRunOutcome.model_validate_json(row[0]) if isinstance(row[0],str) else ReconciliationRunOutcome.model_validate(row[0])
