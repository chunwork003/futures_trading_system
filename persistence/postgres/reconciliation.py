from __future__ import annotations

from typing import Any

from persistence.reconciliation import ReconciliationCaseVersion
from trading.account import BrokerAccount
from trading.reconciliation import ReconciliationCaseError


class PostgresReconciliationCaseRepository:
    """Append-only account-scoped case history；scope drift 與 legacy ambiguity 一律 fail closed。"""
    def __init__(self, connection: Any) -> None: self._connection = connection
    def append(self, version: ReconciliationCaseVersion) -> None:
        with self._connection.cursor() as c:
            c.execute("SELECT broker,account_ref FROM trading.reconciliation_case_history WHERE case_id=%s ORDER BY version DESC LIMIT 1 FOR UPDATE", (version.case_id,))
            prior=c.fetchone()
            scope=(version.reconciliation_case.account.broker,version.reconciliation_case.account.account_ref)
            if prior is not None and tuple(prior) != scope:
                raise ReconciliationCaseError("reconciliation case account scope cannot change")
            c.execute("INSERT INTO trading.reconciliation_case_history (case_id, version, broker, account_ref, recorded_at, state, actor_ref, evidence, case_json) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", (version.case_id, version.version, *scope, version.recorded_at, version.reconciliation_case.state.value, version.actor_ref, list(version.evidence), version.model_dump_json()))
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
